def pytest_collection_modifyitems(items):
    items.sort(key=lambda item: item.get_closest_marker("run_order").args[0])
