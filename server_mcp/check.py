import os
import sys
import importlib
import traceback
import json

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

REQUIRED_FILES = [
    "server.py",
    "mcp_instance.py",
    "tools/basic_math.py",
    "tools/geometry.py",
    "tools/statistics.py",
    "tools/resources.py",
    "tools/prompts.py",
    "tools/server_info.py",
    "tools/utils.py",
]


def ok(msg):
    print(f"[OK] {msg}")


def fail(msg):
    print(f"[FAIL] {msg}")


def warn(msg):
    print(f"[WARN] {msg}")


def check_required_files():
    print("\n=== Проверка наличия необходимых файлов ===")
    all_ok = True

    for path in REQUIRED_FILES:
        full = os.path.join(ROOT, path)
        if os.path.exists(full):
            ok(f"{path} найден")
        else:
            fail(f"{path} отсутствует")
            all_ok = False

    return all_ok


def check_imports():
    print("\n=== Проверка импортов ===")

    try:
        importlib.import_module("mcp_instance")
        ok("mcp_instance импортируется")
    except Exception:
        fail("Ошибка при импорте mcp_instance:")
        traceback.print_exc()
        return False

    modules = [
        "tools.basic_math",
        "tools.geometry",
        "tools.statistics",
        "tools.resources",
        "tools.prompts",
        "tools.server_info",
        "tools.utils",
    ]

    all_ok = True
    for m in modules:
        try:
            importlib.import_module(m)
            ok(f"Модуль {m} импортируется")
        except Exception:
            fail(f"Ошибка импорта {m}:")
            traceback.print_exc()
            all_ok = False

    return all_ok


def check_mcp_tools():
    print("\n=== Проверка регистрации MCP tools ===")

    try:
        inst = importlib.import_module("mcp_instance")
        mcp = inst.mcp
    except Exception:
        fail("Не удалось импортировать mcp_instance.mcp")
        traceback.print_exc()
        return False

    tools = mcp.tools
    prompts = mcp.prompts
    resources = mcp.resources

    if not tools:
        fail("Не найдено ни одного MCP tool")
        return False

    ok(f"Tools зарегистрировано: {len(tools)}")
    for t in tools:
        print(f"  • {t.name}")

    ok(f"Prompts зарегистрировано: {len(prompts)}")
    for p in prompts:
        print(f"  • {p.name}")

    ok(f"Resources зарегистрировано: {len(resources)}")
    for r in resources:
        print(f"  • {r.uri}")

    return True


def check_utils_json():
    print("\n=== Проверка utils.make_success_result / make_error_result ===")

    try:
        utils = importlib.import_module("tools.utils")

        ok_data = utils.make_success_result(
            message="Тест OK",
            data={"value": 42},
            meta={"test": True},
            as_json=False,
        )

        err_data = utils.make_error_result(
            message="Тест ERROR",
            error=ValueError("bad"),
            meta={"test": True},
            as_json=False,
        )

        # Проверка структуры
        for name, obj in [("OK", ok_data), ("ERROR", err_data)]:
            if not isinstance(obj, dict):
                fail(f"{name} результат не dict")
                return False

            for field in ["status", "message", "meta"]:
                if field not in obj:
                    fail(f"{name}: отсутствует обязательное поле {field}")
                    return False

        ok("utils.py корректно формирует ToolResult")
        return True

    except Exception:
        fail("Ошибка в utils.py:")
        traceback.print_exc()
        return False


def main():
    print("=== Диагностика проекта MCP ===")

    f1 = check_required_files()
    f2 = check_imports()
    f3 = check_mcp_tools()
    f4 = check_utils_json()

    print("\n=== Итог ===")
    if f1 and f2 and f3 and f4:
        ok("Проект выглядит корректно 🎉")
        print("Можно запускать MCP-сервер.")
    else:
        fail("Есть проблемы, смотри вывод выше.")


if __name__ == "__main__":
    main()
