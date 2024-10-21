import werkzeug
print(f"Werkzeug version: {werkzeug.__version__}")

import inspect
import werkzeug.urls

print("Available functions in werkzeug.urls:")
for name, obj in inspect.getmembers(werkzeug.urls):
    if inspect.isfunction(obj):
        print(name)