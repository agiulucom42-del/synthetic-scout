import argparse
import json
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict, Any

from core.settings import settings
from core.registry import REGISTRY, TestCase
from core.assertions import TestAssertionError
from core.plugins_loader import load_plugins
from report.reporter import REPORTER, TestResult
from plugins.base import Plugin

log = logging.getLogger("it_tester.runner")


def run_single_test(case: TestCase, plugins: List[Plugin]) -> None:
    import time
    start = time.time()
    try:
        before_count = len(REPORTER.results)
        case.func()
        after_count = len(REPORTER.results)
        if after_count == before_count:
            elapsed_ms = (time.time() - start) * 1000
            result = TestResult(
                name=case.name,
                status="PASSED",
                duration_ms=elapsed_ms,
                tags=case.tags,
            )
            REPORTER.add(result)
            for p in plugins:
                p.on_test_result(result)
    except TestAssertionError as ae:
        elapsed_ms = (time.time() - start) * 1000
        log.warning("[FAILED] %s: %s", case.name, ae)
        result = TestResult(
            name=case.name,
            status="FAILED",
            duration_ms=elapsed_ms,
            tags=case.tags,
            details=str(ae),
        )
        REPORTER.add(result)
        for p in plugins:
            p.on_test_result(result)
    except Exception as e:
        elapsed_ms = (time.time() - start) * 1000
        import traceback
        tb = traceback.format_exc()
        log.error("[ERROR] %s: %s\n%s", case.name, e, tb)
        result = TestResult(
            name=case.name,
            status="ERROR",
            duration_ms=elapsed_ms,
            tags=case.tags,
            details=f"{e}\n{tb}",
        )
        REPORTER.add(result)
        for p in plugins:
            p.on_test_result(result)


def run_tests(tests: List[TestCase], max_workers: int, plugins: List[Plugin]) -> Dict[str, Any]:
    if not tests:
        log.warning("Çalıştırılacak test bulunamadı.")
        return {}

    log.info("ENV=%s | BASE_API_URL=%s", settings.ENV, settings.BASE_API_URL)
    log.info("%s test paralel çalıştırılıyor (max_workers=%s)...", len(tests), max_workers)

    if max_workers < 1:
        max_workers = 1

    context = {
        "env": settings.ENV,
        "base_api_url": settings.BASE_API_URL,
        "test_count": len(tests),
    }
    for p in plugins:
        p.on_start(context)

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(run_single_test, t, plugins): t for t in tests}
        for future in as_completed(futures):
            _ = futures[future]

    summary = REPORTER.summary_dict()
    json_path = REPORTER.save_json()
    summary["summary_file"] = str(json_path)

    for p in plugins:
        p.on_finish(summary)

    return summary


def parse_args(argv: List[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Synthetic Scout")
    parser.add_argument("--list", action="store_true", help="Testleri listele ve çık")
    parser.add_argument(
        "--tag",
        action="append",
        default=[],
        help="Sadece bu tag'e sahip testleri çalıştır (çoklu kullanılabilir)",
    )
    parser.add_argument(
        "--exclude-tag",
        action="append",
        default=[],
        help="Bu tag'e sahip testleri hariç bırak (çoklu)",
    )
    parser.add_argument(
        "--format",
        choices=["json", "junit", "html", "all"],
        default="all",
        help="Çıktı formatı (varsayılan: all)",
    )
    parser.add_argument(
        "--max-workers",
        type=int,
        default=None,
        help="Paralel worker sayısını override et (ENV/MAX_WORKERS yerine)",
    )
    return parser.parse_args(argv[1:])


def main(argv: List[str]) -> int:
    args = parse_args(argv)

    if args.list:
        tests_list = REGISTRY.list_tests()
        print(json.dumps({"tests": tests_list}, indent=2))
        return 0

    tests = REGISTRY.by_tag(args.tag)
    tests = REGISTRY.exclude_tag(tests, args.exclude_tag)

    max_workers = args.max_workers if args.max_workers is not None else settings.MAX_WORKERS
    if max_workers < 1:
        max_workers = 1

    plugins = load_plugins()
    log.info("%s plugin yüklendi.", len(plugins))

    summary = run_tests(tests, max_workers=max_workers, plugins=plugins)

    if not summary:
        print(json.dumps({"message": "no tests to run"}, indent=2))
        return 0

    output_files: Dict[str, str] = {
        "json": summary.get("summary_file", ""),
    }

    if args.format in ("junit", "all"):
        junit_path = REPORTER.save_junit()
        output_files["junit"] = str(junit_path)

    if args.format in ("html", "all"):
        html_path = REPORTER.save_html()
        output_files["html"] = str(html_path)

    summary["outputs"] = output_files

    print(json.dumps(summary, indent=2))

    failed_or_error = summary.get("failed", 0) + summary.get("error", 0)
    return 1 if failed_or_error > 0 else 0
