# Tenacity — Comprehensive API Reference

> A general-purpose retrying library for Python (Apache 2.0).
> Works with synchronous code, asyncio, Trio, and Tornado coroutines.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [The `retry` Decorator](#the-retry-decorator)
- [The `Retrying` / `AsyncRetrying` Classes](#the-retrying--asyncretrying-classes)
- [Stop Strategies](#stop-strategies)
- [Wait Strategies](#wait-strategies)
- [Retry Conditions](#retry-conditions)
- [Before / After / Before-Sleep Callbacks](#before--after--before-sleep-callbacks)
- [Sleep Functions](#sleep-functions)
- [Logging Helpers](#logging-helpers)
- [Context Manager / Iterator Usage](#context-manager--iterator-usage)
- [Async Support](#async-support)
- [RetryCallState](#retrycallstate)
- [Statistics](#statistics)
- [Error Handling](#error-handling)
- [Runtime Reconfiguration](#runtime-reconfiguration)
- [Disabling Retries](#disabling-retries)
- [Generators Warning](#generators-warning)
- [Combining Strategies with Operators](#combining-strategies-with-operators)
- [Custom Callbacks](#custom-callbacks)
- [Async Retry Strategies](#async-retry-strategies)
- [Tornado Support](#tornado-support)
- [Time Unit Support](#time-unit-support)
- [Complete `__all__` Exports](#complete-__all__-exports)

---

## Installation

```bash
pip install tenacity
```

---

## Quick Start

```python
from tenacity import retry

@retry
def do_something_unreliable():
    # Retries forever on any Exception, no wait between retries
    ...
```

With options:

```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(stop=stop_after_attempt(5), wait=wait_exponential(multiplier=1, min=1, max=10))
def call_api():
    ...
```

---

## The `retry` Decorator

```python
tenacity.retry(
    func=None,                    # If passed directly, wraps with defaults: @retry
    *,
    sleep=tenacity.sleep,         # Callable[[float], None] — sleep function
    stop=stop_never,              # StopBaseT — when to give up
    wait=wait_none(),             # WaitBaseT — how long between retries
    retry=retry_if_exception_type(),  # RetryBaseT — when to retry
    before=before_nothing,        # Callable[[RetryCallState], None]
    after=after_nothing,          # Callable[[RetryCallState], None]
    before_sleep=None,            # Callable[[RetryCallState], None] | None
    reraise=False,                # bool — reraise last exception instead of RetryError
    retry_error_cls=RetryError,   # type[RetryError] — custom error class
    retry_error_callback=None,    # Callable[[RetryCallState], Any] | None
    enabled=True,                 # bool — set False to bypass retry logic entirely
)
```

### Usage Forms

```python
# Form 1: No arguments — retries forever on any Exception
@retry
def f(): ...

# Form 2: With keyword arguments
@retry(stop=stop_after_attempt(3))
def f(): ...

# Form 3: Wrapping an existing function
retrying = Retrying(stop=stop_after_attempt(3))
result = retrying(my_func, arg1, arg2, kwarg1=val)
```

### Auto-detection

The `@retry` decorator automatically selects the right retrying class:
- **`Retrying`** — for regular synchronous functions
- **`AsyncRetrying`** — for `async def` functions (or when `sleep` is a coroutine)
- **`TornadoRetrying`** — for Tornado coroutines (when tornado is installed)

### Attributes on Decorated Functions

After decorating with `@retry`, the wrapped function gains:

| Attribute | Type | Description |
|-----------|------|-------------|
| `.retry` | `BaseRetrying` | The retrying controller instance |
| `.statistics` | `dict[str, Any]` | Runtime statistics from the most recent call |
| `.retry_with(**kw)` | method | Returns a new decorated function with modified retry settings |

---

## The `Retrying` / `AsyncRetrying` Classes

### `Retrying` (synchronous)

```python
tenacity.Retrying(
    sleep: Callable[[float], None] = tenacity.sleep,
    stop: StopBaseT = stop_never,
    wait: WaitBaseT = wait_none(),
    retry: RetryBaseT = retry_if_exception_type(),
    before: Callable[[RetryCallState], None] = before_nothing,
    after: Callable[[RetryCallState], None] = after_nothing,
    before_sleep: Callable[[RetryCallState], None] | None = None,
    reraise: bool = False,
    retry_error_cls: type[RetryError] = RetryError,
    retry_error_callback: Callable[[RetryCallState], Any] | None = None,
    name: str | None = None,
    enabled: bool = True,
)
```

**Key methods:**

| Method | Description |
|--------|-------------|
| `__call__(fn, *args, **kwargs)` | Execute `fn` with retry logic |
| `wraps(fn)` | Return a decorated version of `fn` |
| `copy(**overrides)` | Clone this instance with changed parameters |
| `begin()` | Reset statistics for a new retry session |

**Key properties:**

| Property | Type | Description |
|----------|------|-------------|
| `statistics` | `dict[str, Any]` | Thread-local runtime statistics |

### `AsyncRetrying`

```python
tenacity.AsyncRetrying(
    sleep: Callable[[float], Awaitable[None]] = _portable_async_sleep,
    stop: StopBaseT = stop_never,
    wait: WaitBaseT = wait_none(),
    retry: RetryBaseT = retry_if_exception_type(),
    before: Callable[[RetryCallState], None | Awaitable[None]] = before_nothing,
    after: Callable[[RetryCallState], None | Awaitable[None]] = after_nothing,
    before_sleep: Callable[[RetryCallState], None | Awaitable[None]] | None = None,
    reraise: bool = False,
    retry_error_cls: type[RetryError] = RetryError,
    retry_error_callback: Callable[[RetryCallState], Any | Awaitable[Any]] | None = None,
    name: str | None = None,
    enabled: bool = True,
)
```

- Automatically detects asyncio vs Trio (via `sniffio`)
- `before`, `after`, `before_sleep`, and `retry_error_callback` may be sync or async
- Supports `async for attempt in AsyncRetrying(...):`

---

## Stop Strategies

All stop strategies accept a `RetryCallState` and return `bool` (True = stop retrying).

### `stop_never`

```python
tenacity.stop_never  # singleton instance
```
Never stops — retries forever. This is the **default**.

### `stop_after_attempt`

```python
tenacity.stop_after_attempt(max_attempt_number: int)
```
Stop after `max_attempt_number` attempts. The count includes the initial call.

```python
@retry(stop=stop_after_attempt(5))  # tries up to 5 times total
def f(): ...
```

### `stop_after_delay`

```python
tenacity.stop_after_delay(max_delay: int | float | timedelta)
```
Stop when total elapsed time from first attempt >= `max_delay` seconds.

**Note:** The actual total time may *exceed* `max_delay` because the check happens after the last sleep completes. If strict timing is needed, use `stop_before_delay`.

```python
@retry(stop=stop_after_delay(30))          # stop after 30 seconds
@retry(stop=stop_after_delay(timedelta(minutes=1)))  # also accepts timedelta
```

### `stop_before_delay`

```python
tenacity.stop_before_delay(max_delay: int | float | timedelta)
```
Stop *before* the next attempt if `elapsed + upcoming_sleep >= max_delay`. Ensures the total time never exceeds the limit.

```python
@retry(stop=stop_before_delay(10), wait=wait_exponential())
def f(): ...  # guaranteed to not retry past 10s
```

### `stop_when_event_set`

```python
tenacity.stop_when_event_set(event: threading.Event)
```
Stop when a `threading.Event` is set. Useful for graceful shutdown.

```python
import threading
shutdown = threading.Event()

@retry(stop=stop_when_event_set(shutdown))
def poll():
    ...

# From another thread:
shutdown.set()  # will stop retrying
```

### Combining Stop Strategies

Use `|` (OR — stop if *any* condition is met) or `&` (AND — stop only if *all* are met):

```python
@retry(stop=stop_after_attempt(5) | stop_after_delay(30))
def f(): ...  # stop after 5 attempts OR 30 seconds, whichever comes first
```

---

## Wait Strategies

All wait strategies accept a `RetryCallState` and return `float` (seconds to sleep).

### `wait_none`

```python
tenacity.wait_none()
```
No wait between retries (0 seconds). This is the **default**.

### `wait_fixed`

```python
tenacity.wait_fixed(wait: int | float | timedelta)
```
Wait a fixed number of seconds between retries.

```python
@retry(wait=wait_fixed(2))           # 2 seconds
@retry(wait=wait_fixed(timedelta(seconds=0.5)))  # 500ms
```

### `wait_random`

```python
tenacity.wait_random(
    min: int | float | timedelta = 0,
    max: int | float | timedelta = 1,
)
```
Wait a random time uniformly distributed between `min` and `max` seconds.

```python
@retry(wait=wait_random(min=1, max=3))
```

### `wait_exponential`

```python
tenacity.wait_exponential(
    multiplier: float = 1,
    max: int | float | timedelta = MAX_WAIT,  # ~4.6e18
    exp_base: float = 2,
    min: int | float | timedelta = 0,
)
```

Formula: `max(min, min(multiplier * exp_base^(attempt-1), max))`

| Attempt | Default (mult=1, base=2, min=0) |
|---------|-------------------------------|
| 1 | 1s |
| 2 | 2s |
| 3 | 4s |
| 4 | 8s |
| 5 | 16s |

**No jitter** — intervals are deterministic. Good for single-client backoff, not for contention resolution (use `wait_random_exponential` for that).

```python
@retry(wait=wait_exponential(multiplier=1, min=4, max=60))
```

### `wait_random_exponential` / `wait_full_jitter`

```python
tenacity.wait_random_exponential(
    multiplier: float = 1,
    max: int | float | timedelta = MAX_WAIT,
    exp_base: float = 2,
    min: int | float | timedelta = 0,
)
```

Also available as `wait_full_jitter` (alias).

Formula: `uniform(min, min(multiplier * exp_base^(attempt-1), max))`

Implements the "Full Jitter" algorithm from [AWS Architecture Blog](https://aws.amazon.com/blogs/architecture/exponential-backoff-and-jitter/). Best for resolving contention between multiple processes for a shared resource.

```python
@retry(wait=wait_random_exponential(multiplier=1, max=60))
```

### `wait_exponential_jitter`

```python
tenacity.wait_exponential_jitter(
    initial: float = 1,         # DEPRECATED — use multiplier instead
    max: int | float | timedelta = MAX_WAIT,
    exp_base: float = 2,
    jitter: int | float | timedelta = 1,
    min: int | float | timedelta = 0,
    multiplier: float = 1,
)
```

Formula: `max(min, min(multiplier * exp_base^(attempt-1) + uniform(0, jitter), max))`

Implements the [Google Cloud retry strategy](https://cloud.google.com/storage/docs/retry-strategy). Differs from `wait_random_exponential` in that jitter is *added* to the exponential value rather than being the full range.

**Note:** `initial` is deprecated. Use `multiplier` instead. You cannot specify both.

```python
@retry(wait=wait_exponential_jitter(multiplier=1, jitter=2, max=60))
```

### `wait_incrementing`

```python
tenacity.wait_incrementing(
    start: int | float | timedelta = 0,
    increment: int | float | timedelta = 100,
    max: int | float | timedelta = MAX_WAIT,
)
```

Formula: `min(start + increment * (attempt - 1), max)`

Linear increase. Note the default `increment=100` is in seconds.

```python
@retry(wait=wait_incrementing(start=1, increment=2, max=30))
# waits: 1, 3, 5, 7, ... up to 30
```

### `wait_chain`

```python
tenacity.wait_chain(*strategies: wait_base)
```
Apply different wait strategies sequentially. After all strategies are exhausted, the last one is used for all subsequent attempts.

```python
@retry(wait=wait_chain(
    *[wait_fixed(1) for _ in range(3)] +   # 1s for first 3 attempts
    *[wait_fixed(5) for _ in range(2)] +   # 5s for next 2 attempts
    [wait_fixed(10)]                        # 10s thereafter
))
```

### `wait_combine`

```python
tenacity.wait_combine(*strategies: wait_base)
```
Sum the results of multiple wait strategies.

```python
@retry(wait=wait_combine(wait_fixed(1), wait_random(0, 2)))
# waits: 1 + random(0,2) seconds each time
```

### `wait_exception`

```python
tenacity.wait_exception(predicate: Callable[[BaseException], float])
```
Wait time determined by inspecting the raised exception. The predicate receives the exception and returns seconds to wait.

```python
def http_error_wait(exception):
    if isinstance(exception, requests.HTTPError):
        if exception.response.status_code == 429:
            return float(exception.response.headers.get("Retry-After", "1"))
    return 60.0

@retry(stop=stop_after_attempt(3), wait=wait_exception(http_error_wait))
def api_call():
    response = requests.get(url)
    response.raise_for_status()
```

### Combining Wait Strategies

Use `+` to sum wait times from multiple strategies:

```python
@retry(wait=wait_fixed(3) + wait_random(0, 2))
def f(): ...  # waits 3–5 seconds each retry
```

---

## Retry Conditions

All retry conditions accept a `RetryCallState` and return `bool` (True = should retry).

### `retry_if_exception_type` (default)

```python
tenacity.retry_if_exception_type(
    exception_types: type[BaseException] | tuple[type[BaseException], ...] = Exception
)
```
Retry if the raised exception is an instance of the given type(s).

```python
@retry(retry=retry_if_exception_type(IOError))
@retry(retry=retry_if_exception_type((IOError, ConnectionError)))
```

### `retry_if_not_exception_type`

```python
tenacity.retry_if_not_exception_type(
    exception_types: type[BaseException] | tuple[type[BaseException], ...] = Exception
)
```
Retry on any exception *except* the given type(s).

```python
@retry(retry=retry_if_not_exception_type(ValueError))
# Retries on everything except ValueError
```

### `retry_unless_exception_type`

```python
tenacity.retry_unless_exception_type(
    exception_types: type[BaseException] | tuple[type[BaseException], ...] = Exception
)
```
Retry on *success or* on exceptions that are NOT the given type. Stops only when an exception of the specified type is raised.

```python
@retry(retry=retry_unless_exception_type(KeyboardInterrupt))
# Retries forever (even on success!), stops only on KeyboardInterrupt
```

### `retry_if_exception`

```python
tenacity.retry_if_exception(predicate: Callable[[BaseException], bool])
```
Retry if the exception satisfies a custom predicate.

```python
@retry(retry=retry_if_exception(lambda e: "timeout" in str(e).lower()))
```

### `retry_if_exception_message`

```python
tenacity.retry_if_exception_message(
    message: str | None = None,    # exact match
    match: str | re.Pattern | None = None,  # regex match (anchored at start)
)
```
Retry if the exception's string representation matches. Provide either `message` (exact) or `match` (regex), not both.

```python
@retry(retry=retry_if_exception_message(match=r".*timeout.*"))
@retry(retry=retry_if_exception_message(message="Connection refused"))
```

### `retry_if_not_exception_message`

```python
tenacity.retry_if_not_exception_message(
    message: str | None = None,
    match: str | re.Pattern | None = None,
)
```
Retry unless the exception message matches. Also retries on success (no exception).

### `retry_if_exception_cause_type`

```python
tenacity.retry_if_exception_cause_type(
    exception_types: type[BaseException] | tuple[type[BaseException], ...] = Exception
)
```
Retry if any exception in the `__cause__` chain matches the given type(s). Walks the chain recursively.

```python
@retry(retry=retry_if_exception_cause_type(ConnectionError))
def f():
    try:
        connect()
    except ConnectionError as e:
        raise RuntimeError("wrapped") from e
```

### `retry_if_result`

```python
tenacity.retry_if_result(predicate: Callable[[Any], bool])
```
Retry if the return value satisfies the predicate (predicate returns True).

```python
@retry(retry=retry_if_result(lambda x: x is None))
def f():
    return None  # will keep retrying
```

### `retry_if_not_result`

```python
tenacity.retry_if_not_result(predicate: Callable[[Any], bool])
```
Retry if the return value does *not* satisfy the predicate.

```python
@retry(retry=retry_if_not_result(lambda x: x == 200))
def get_status():
    return requests.get(url).status_code
```

### `retry_always`

```python
tenacity.retry_always  # singleton instance
```
Always retry (returns True for every outcome).

### `retry_never`

```python
tenacity.retry_never  # singleton instance
```
Never retry (returns False for every outcome).

### `retry_any`

```python
tenacity.retry_any(*retries: RetryBaseT)
```
Retry if *any* of the given conditions is True (OR logic).

### `retry_all`

```python
tenacity.retry_all(*retries: RetryBaseT)
```
Retry only if *all* of the given conditions are True (AND logic).

### Combining Retry Conditions

Use `|` (OR) and `&` (AND) operators:

```python
@retry(retry=retry_if_result(lambda x: x is None) | retry_if_exception_type())
def f(): ...  # retry on None result OR on any exception

@retry(retry=retry_if_exception_type(IOError) & retry_if_exception_message(match="temp"))
def f(): ...  # retry only on IOError with "temp" in the message
```

---

## Before / After / Before-Sleep Callbacks

These callbacks receive a `RetryCallState` argument and return `None`.

### `before` — runs before each attempt

```python
before=before_nothing          # default, does nothing
before=before_log(logger, logging.DEBUG)  # logs "Starting call to..."
before=my_custom_function      # any Callable[[RetryCallState], None]
```

### `after` — runs after each failed attempt (before deciding whether to retry)

```python
after=after_nothing            # default, does nothing
after=after_log(logger, logging.DEBUG)  # logs "Finished call to..."
after=my_custom_function       # any Callable[[RetryCallState], None]
```

### `before_sleep` — runs after a failed attempt, right before sleeping (only on retries)

```python
before_sleep=None                                    # default, nothing
before_sleep=before_sleep_log(logger, logging.DEBUG)  # logs retry info
before_sleep=my_reconnect_function                    # e.g. re-establish connection
```

The `before_sleep` callback is ideal for:
- Logging retries
- Reconnecting to services
- Refreshing tokens
- Any setup needed before the next attempt

---

## Sleep Functions

### `sleep` (default)

```python
tenacity.sleep(seconds: float) -> None
```
Wraps `time.sleep()`. Can be mocked for testing.

### `sleep_using_event`

```python
tenacity.sleep_using_event(event: threading.Event)
```
A callable class that waits on an event instead of sleeping. If the event is set early, it ejects from sleep.

```python
import threading
cancel = threading.Event()

@retry(sleep=sleep_using_event(cancel), stop=stop_when_event_set(cancel))
def poll():
    ...

# From another thread:
cancel.set()  # immediately wakes up and stops
```

---

## Logging Helpers

### `before_log`

```python
tenacity.before_log(logger: LoggerProtocol, log_level: int) -> Callable
```
Returns a `before` callback that logs: `"Starting call to '{fn}', this is the {n}th time calling it."`

### `after_log`

```python
tenacity.after_log(
    logger: LoggerProtocol,
    log_level: int,
    sec_format: str = "%.3g",
) -> Callable
```
Returns an `after` callback that logs: `"Finished call to '{fn}' after {sec}(s), this was the {n}th time calling it."`

### `before_sleep_log`

```python
tenacity.before_sleep_log(
    logger: LoggerProtocol,
    log_level: int,
    exc_info: bool = False,
    sec_format: str = "%.3g",
) -> Callable
```
Returns a `before_sleep` callback that logs: `"Retrying {fn} in {sec} seconds as it {raised/returned} {value}."`

When `exc_info=True`, the full traceback is appended to the log message.

### `LoggerProtocol`

Any object with a `.log(level: int, msg: str, *args)` method. Compatible with `logging`, `structlog`, `loguru`, etc.

---

## Context Manager / Iterator Usage

### Synchronous

```python
from tenacity import Retrying, stop_after_attempt

for attempt in Retrying(stop=stop_after_attempt(3)):
    with attempt:
        result = do_something()  # exceptions are caught and trigger retry
```

The `AttemptManager` context manager catches exceptions and feeds them back to the retry logic. If all retries are exhausted, `RetryError` is raised.

Access attempt info via `attempt.retry_state`:
```python
for attempt in Retrying(stop=stop_after_attempt(3)):
    with attempt:
        print(f"Attempt #{attempt.retry_state.attempt_number}")
        result = do_something()
```

### Async

```python
from tenacity import AsyncRetrying, stop_after_attempt

async for attempt in AsyncRetrying(stop=stop_after_attempt(3)):
    with attempt:
        result = await do_something_async()
```

### Setting Results in Context Manager Mode

When using `retry_if_result` with the context manager, you need to manually set the result:

```python
async for attempt in AsyncRetrying(retry=retry_if_result(lambda x: x < 3)):
    with attempt:
        result = compute()
    if not attempt.retry_state.outcome.failed:
        attempt.retry_state.set_result(result)
```

---

## Async Support

### asyncio / Trio

The `@retry` decorator automatically detects async functions and uses `AsyncRetrying`:

```python
@retry
async def my_async_function():
    await some_coroutine()
```

Trio is auto-detected via `sniffio`. You can also explicitly pass the sleep function:

```python
@retry(sleep=trio.sleep)
async def my_trio_function():
    ...
```

### Async Retry Strategies

The `tenacity.asyncio.retry` module provides async versions of retry strategies where the predicate itself is async:

```python
from tenacity.asyncio.retry import retry_if_exception, retry_if_result

# The predicate can be an async function
@retry(retry=retry_if_result(my_async_predicate))
async def f(): ...
```

Available in `tenacity.asyncio.retry`:
- `async_retry_base` — abstract base for async retry strategies
- `retry_if_exception(predicate: Callable[[BaseException], Awaitable[bool]])`
- `retry_if_result(predicate: Callable[[Any], Awaitable[bool]])`
- `retry_any(*retries)` — async OR combinator
- `retry_all(*retries)` — async AND combinator

### Async Callbacks

With `AsyncRetrying`, the `before`, `after`, `before_sleep`, and `retry_error_callback` parameters accept either sync or async callables. They are automatically wrapped if needed.

---

## RetryCallState

`RetryCallState` is the object passed to all callbacks. It contains full context about the current retry session.

```python
class RetryCallState:
    start_time: float              # time.monotonic() when retrying began
    retry_object: BaseRetrying     # the Retrying instance
    fn: Callable | None            # the wrapped function (None in context-manager mode)
    args: tuple                    # positional args passed to the function
    kwargs: dict                   # keyword args passed to the function
    attempt_number: int            # current attempt (starts at 1)
    outcome: Future | None         # last result/exception (None before first attempt)
    outcome_timestamp: float | None  # timestamp of last outcome
    idle_for: float                # total seconds spent sleeping
    next_action: RetryAction | None  # decided by retry manager
    upcoming_sleep: float          # seconds until next attempt
```

### Key Properties and Methods

| Member | Type | Description |
|--------|------|-------------|
| `seconds_since_start` | `float \| None` | `outcome_timestamp - start_time`. `None` if no outcome yet |
| `get_fn_name()` | `str` | Fully-qualified name of the wrapped function, or `<unknown>` |
| `outcome.result()` | `Any` | The return value (raises if it was an exception) |
| `outcome.exception()` | `BaseException \| None` | The exception, or `None` if successful |
| `outcome.failed` | `bool` | `True` if an exception was raised |

---

## Statistics

The `statistics` dict is available on both the decorated function and the `Retrying` instance:

```python
@retry(stop=stop_after_attempt(3))
def f(): ...

try:
    f()
except Exception:
    pass

print(f.statistics)
```

### Statistics Keys

| Key | Type | Description |
|-----|------|-------------|
| `"start_time"` | `float` | `time.monotonic()` timestamp when retrying began |
| `"attempt_number"` | `int` | Total number of attempts made |
| `"idle_for"` | `float` | Total seconds spent sleeping between attempts |
| `"delay_since_first_attempt"` | `float` | Elapsed seconds from start to last outcome |

**Note:** Statistics are thread-local. Each thread gets its own view.

---

## Error Handling

### `RetryError`

```python
class RetryError(Exception):
    last_attempt: Future  # the final attempt's outcome
```

Raised when all retries are exhausted (unless `reraise=True` or `retry_error_callback` is set).

**Methods:**

| Method | Description |
|--------|-------------|
| `reraise()` | Re-raises the original exception from `last_attempt` |

### `reraise=True`

When set, the *original* exception is re-raised instead of `RetryError`, making it appear at the end of the stack trace:

```python
@retry(reraise=True, stop=stop_after_attempt(3))
def f():
    raise ValueError("bad")

try:
    f()
except ValueError:  # catches the original exception, not RetryError
    pass
```

### `retry_error_callback`

A callable invoked when retries are exhausted, *instead* of raising `RetryError`:

```python
def return_last(retry_state):
    return retry_state.outcome.result()

@retry(stop=stop_after_attempt(3), retry_error_callback=return_last, retry=retry_if_result(lambda x: x is None))
def f():
    return None  # after 3 attempts, returns None instead of raising
```

### `retry_error_cls`

Override the exception class raised on exhaustion (must subclass `RetryError`):

```python
class MyRetryError(RetryError):
    pass

@retry(stop=stop_after_attempt(3), retry_error_cls=MyRetryError)
def f():
    raise Exception("fail")
```

### `TryAgain`

```python
class TryAgain(Exception):
    """Raise inside a retried function to force an immediate retry."""
```

Raising `TryAgain` always triggers a retry, regardless of the `retry` condition:

```python
@retry
def f():
    result = check_something()
    if result == "not ready":
        raise TryAgain
    return result
```

---

## Runtime Reconfiguration

### `retry_with`

Create a modified copy of a decorated function:

```python
@retry(stop=stop_after_attempt(3))
def f(): ...

# Returns a new decorated function with different settings
g = f.retry_with(stop=stop_after_attempt(10))
g()
```

### Patching `retry` Attribute

For temporary changes (e.g., in tests), patch the `.retry` attribute:

```python
from unittest import mock

@retry(stop=stop_after_attempt(3), wait=wait_fixed(3))
def f(): ...

with mock.patch.object(f.retry, "wait", wait_fixed(0)):
    try:
        f()  # no wait between retries during test
    except Exception:
        pass
```

**Note:** `.retry` is write-only for configuration. Read statistics from `.statistics`.

### Direct `Retrying` Usage

```python
def my_func(x, y):
    ...

retryer = Retrying(stop=stop_after_attempt(5), reraise=True)
result = retryer(my_func, 1, 2)
```

---

## Disabling Retries

Set `enabled=False` to bypass all retry logic — the function is called directly:

```python
import os

@retry(
    enabled=os.getenv("ENABLE_RETRIES", "1") != "0",
    stop=stop_after_attempt(5),
    wait=wait_fixed(1),
)
def call_api():
    ...
```

Per-call disable:

```python
call_api.retry_with(enabled=False)()
```

---

## Generators Warning

`@retry` does **not** support generator or async generator functions. Decorating a generator wraps only the call that *creates* the generator object, not the iteration.

Also, generators passed as *arguments* to a retried function will be exhausted after the first attempt:

```python
# BAD: generator exhausted after first attempt
@retry
def process(items):
    for item in items:
        do_work(item)
process(my_generator())  # retries see empty generator

# GOOD: pass a factory
@retry
def process(items_factory):
    for item in items_factory():
        do_work(item)
process(my_generator)  # fresh generator on each retry
```

---

## Combining Strategies with Operators

### Stop: `|` and `&`

```python
stop_after_attempt(5) | stop_after_delay(30)   # stop_any: either condition
stop_after_attempt(5) & stop_after_delay(30)   # stop_all: both conditions
```

### Wait: `+`

```python
wait_fixed(1) + wait_random(0, 2)  # wait_combine: sum of both
```

### Retry: `|` and `&`

```python
retry_if_exception_type(IOError) | retry_if_result(lambda x: x is None)  # retry_any
retry_if_exception_type(IOError) & retry_if_exception_message(match="temp")  # retry_all
```

---

## Custom Callbacks

All callback signatures:

```python
def my_stop(retry_state: RetryCallState) -> bool:
    """Return True to stop retrying."""
    ...

def my_wait(retry_state: RetryCallState) -> float:
    """Return seconds to wait before next attempt."""
    ...

def my_retry(retry_state: RetryCallState) -> bool:
    """Return True to retry, False to accept the result/exception."""
    ...

def my_before(retry_state: RetryCallState) -> None:
    """Called before each attempt."""
    ...

def my_after(retry_state: RetryCallState) -> None:
    """Called after each failed attempt."""
    ...

def my_before_sleep(retry_state: RetryCallState) -> None:
    """Called after a failed attempt, just before sleeping."""
    ...

def my_retry_error_callback(retry_state: RetryCallState) -> Any:
    """Called when retries are exhausted. Return value becomes the function's return value."""
    ...
```

---

## Tornado Support

When `tornado` is installed, `@retry` auto-detects Tornado coroutines:

```python
@retry
async def my_tornado_handler(http_client, url):
    await http_client.fetch(url)
```

The `TornadoRetrying` class uses `tornado.gen.sleep` by default.

---

## Time Unit Support

Many parameters (`wait`, `stop`, `min`, `max`, etc.) accept `int | float | timedelta`:

```python
from datetime import timedelta

@retry(
    wait=wait_fixed(timedelta(milliseconds=500)),
    stop=stop_after_delay(timedelta(minutes=2)),
)
def f(): ...
```

The `_utils.to_seconds()` function handles conversion. `timedelta` objects call `.total_seconds()`.

---

## Complete `__all__` Exports

All public names from `tenacity`:

| Name | Category |
|------|----------|
| `retry` | Decorator |
| `Retrying` | Sync controller |
| `AsyncRetrying` | Async controller |
| `BaseRetrying` | Base class |
| `RetryCallState` | State object |
| `RetryError` | Exception |
| `TryAgain` | Exception |
| `Future` | Result wrapper |
| `AttemptManager` | Context manager |
| `BaseAction`, `RetryAction` | Internal |
| `DoAttempt`, `DoSleep` | Internal |
| `NO_RESULT` | Sentinel |
| `WrappedFn` | Type alias |
| **Stop** | |
| `stop_never` | Never stop (default) |
| `stop_after_attempt` | Stop after N attempts |
| `stop_after_delay` | Stop after elapsed time |
| `stop_before_delay` | Stop before exceeding time limit |
| `stop_when_event_set` | Stop on threading.Event |
| `stop_any` | OR combinator |
| `stop_all` | AND combinator |
| **Wait** | |
| `wait_none` | No wait (default) |
| `wait_fixed` | Fixed delay |
| `wait_random` | Random uniform delay |
| `wait_exponential` | Exponential backoff (no jitter) |
| `wait_random_exponential` | Full jitter exponential |
| `wait_full_jitter` | Alias for `wait_random_exponential` |
| `wait_exponential_jitter` | Exponential + additive jitter |
| `wait_incrementing` | Linear increase |
| `wait_chain` | Sequential strategies |
| `wait_combine` | Sum of strategies |
| `wait_exception` | Wait based on exception inspection |
| **Retry** | |
| `retry_if_exception_type` | Retry on exception type (default) |
| `retry_if_not_exception_type` | Retry except on type |
| `retry_unless_exception_type` | Retry until exception type |
| `retry_if_exception` | Retry on predicate(exception) |
| `retry_if_exception_message` | Retry on message match |
| `retry_if_not_exception_message` | Retry unless message match |
| `retry_if_exception_cause_type` | Retry on cause chain type |
| `retry_if_result` | Retry on result predicate |
| `retry_if_not_result` | Retry unless result predicate |
| `retry_always` | Always retry |
| `retry_never` | Never retry |
| `retry_any` | OR combinator |
| `retry_all` | AND combinator |
| `retry_base` | Abstract base |
| **Callbacks** | |
| `before_log` | Log before attempt |
| `before_nothing` | No-op before |
| `after_log` | Log after attempt |
| `after_nothing` | No-op after |
| `before_sleep_log` | Log before sleep |
| `before_sleep_nothing` | No-op before sleep |
| **Sleep** | |
| `sleep` | Default `time.sleep` wrapper |
| `sleep_using_event` | Sleep via `threading.Event` |
