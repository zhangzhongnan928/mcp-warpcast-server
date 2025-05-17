import os
import importlib
import inspect
import asyncio

class MonkeyPatch:
    def __init__(self):
        self._actions = []

    def setattr(self, obj, name, value):
        orig = getattr(obj, name)
        self._actions.append((obj, name, orig))
        setattr(obj, name, value)

    def setitem(self, mapping, key, value):
        orig = mapping.get(key)
        self._actions.append((mapping, key, orig, True if key in mapping else False))
        mapping[key] = value

    def setenv(self, key, value):
        orig = os.environ.get(key)
        existed = key in os.environ
        self._actions.append((os.environ, key, orig, existed))
        os.environ[key] = value

    def delenv(self, key, raising=True):
        existed = key in os.environ
        orig = os.environ.get(key)
        if existed:
            del os.environ[key]
        elif raising:
            raise KeyError(key)
        self._actions.append((os.environ, key, orig, existed))

    def undo(self):
        for item in reversed(self._actions):
            if len(item) == 3:
                obj, name, orig = item
                setattr(obj, name, orig)
            else:
                mapping, key, orig, existed = item
                if existed:
                    mapping[key] = orig
                else:
                    mapping.pop(key, None)
        self._actions.clear()


def run_func(func):
    sig = inspect.signature(func)
    kwargs = {}
    mp = None
    if 'monkeypatch' in sig.parameters:
        mp = MonkeyPatch()
        kwargs['monkeypatch'] = mp
    try:
        if inspect.iscoroutinefunction(func):
            asyncio.run(func(**kwargs))
        else:
            func(**kwargs)
        result = True
    except Exception as e:
        print(f"FAILED: {func.__name__}: {e}")
        result = False
    finally:
        if mp:
            mp.undo()
    return result


def main():
    failed = 0
    for filename in os.listdir('tests'):
        if filename.startswith('test_') and filename.endswith('.py'):
            module = importlib.import_module(f'tests.{filename[:-3]}')
            for name, func in inspect.getmembers(module, inspect.isfunction):
                if name.startswith('test_'):
                    print(f'running {filename}:{name}')
                    if not run_func(func):
                        failed += 1
    if failed:
        print(f'{failed} tests failed')
        raise SystemExit(1)
    print('all tests passed')

if __name__ == '__main__':
    main()
