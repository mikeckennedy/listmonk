# Pydantic V2 Comprehensive Reference

> Generated from source code and documentation of Pydantic 2.13.x.
> For use by AI systems and developers building with Pydantic.

---

## Table of Contents

1. [Installation & Version](#installation--version)
2. [BaseModel](#basemodel)
3. [Fields](#fields)
4. [Validators](#validators)
5. [Serializers](#serializers)
6. [Configuration (ConfigDict)](#configuration-configdict)
7. [Types](#types)
8. [Network Types](#network-types)
9. [JSON Schema](#json-schema)
10. [TypeAdapter](#typeadapter)
11. [RootModel](#rootmodel)
12. [Dataclasses](#dataclasses)
13. [Aliases](#aliases)
14. [validate_call](#validate_call)
15. [Errors](#errors)
16. [Experimental: Pipeline API](#experimental-pipeline-api)
17. [Performance Tips](#performance-tips)
18. [Strict Mode](#strict-mode)
19. [Unions](#unions)

---

## Installation & Version

```bash
pip install pydantic
# Optional extras:
pip install pydantic[email]   # email validation via email-validator
pip install pydantic-settings  # settings management
```

Current version: `2.13.x`

```python
from pydantic import __version__, VERSION
from pydantic.version import version_short, version_info
```

---

## BaseModel

The foundation of Pydantic. Define data models by subclassing `BaseModel`.

### Basic Usage

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str | None = None

user = User(name='Alice', age=30)
```

### Class Signature

```python
class BaseModel(metaclass=ModelMetaclass):
    model_config: ClassVar[ConfigDict]

    # Internal class vars (read-only)
    __pydantic_fields__: ClassVar[dict[str, FieldInfo]]
    __pydantic_computed_fields__: ClassVar[dict[str, ComputedFieldInfo]]
    __pydantic_core_schema__: ClassVar[CoreSchema]
    __pydantic_validator__: ClassVar[SchemaValidator]
    __pydantic_serializer__: ClassVar[SchemaSerializer]
    __pydantic_complete__: ClassVar[bool]
    __pydantic_root_model__: ClassVar[bool]

    # Instance vars
    __pydantic_extra__: dict[str, Any] | None      # Extra fields (when extra='allow')
    __pydantic_fields_set__: set[str]               # Fields explicitly set at init
    __pydantic_private__: dict[str, Any] | None     # Private attribute values
```

### Constructor

```python
def __init__(self, /, **data: Any) -> None
```

### Validation Class Methods

```python
@classmethod
def model_validate(
    cls,
    obj: Any,
    *,
    strict: bool | None = None,
    extra: Literal['allow', 'ignore', 'forbid'] | None = None,
    from_attributes: bool | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> Self
```

Validate a Python object (dict, object with attributes, etc.).

```python
@classmethod
def model_validate_json(
    cls,
    json_data: str | bytes | bytearray,
    *,
    strict: bool | None = None,
    extra: Literal['allow', 'ignore', 'forbid'] | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> Self
```

Validate JSON data directly (faster than `json.loads()` + `model_validate()`).

```python
@classmethod
def model_validate_strings(
    cls,
    obj: Any,
    *,
    strict: bool | None = None,
    extra: Literal['allow', 'ignore', 'forbid'] | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> Self
```

Validate with string coercion (useful for form data).

### Construction Without Validation

```python
@classmethod
def model_construct(
    cls,
    _fields_set: set[str] | None = None,
    **values: Any,
) -> Self
```

Create model instance **without validation**. Use when data is already trusted.

### Serialization Instance Methods

```python
def model_dump(
    self,
    *,
    mode: Literal['json', 'python'] | str = 'python',
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    exclude_computed_fields: bool = False,
    round_trip: bool = False,
    warnings: bool | Literal['none', 'warn', 'error'] = True,
    fallback: Callable[[Any], Any] | None = None,
    serialize_as_any: bool = False,
    polymorphic_serialization: bool | None = None,
) -> dict[str, Any]
```

Serialize to Python dict. Use `mode='json'` for JSON-compatible types (e.g., datetime -> str).

```python
def model_dump_json(
    self,
    *,
    indent: int | None = None,
    ensure_ascii: bool = False,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    exclude_computed_fields: bool = False,
    round_trip: bool = False,
    warnings: bool | Literal['none', 'warn', 'error'] = True,
    fallback: Callable[[Any], Any] | None = None,
    serialize_as_any: bool = False,
    polymorphic_serialization: bool | None = None,
) -> str
```

Serialize directly to JSON string.

### Copy

```python
def model_copy(
    self,
    *,
    update: Mapping[str, Any] | None = None,
    deep: bool = False,
) -> Self
```

Copy model, optionally updating fields. `deep=True` for deep copy.

### JSON Schema

```python
@classmethod
def model_json_schema(
    cls,
    by_alias: bool = True,
    ref_template: str = '#/$defs/{model}',
    schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
    mode: Literal['validation', 'serialization'] = 'validation',
    *,
    union_format: Literal['any_of', 'primitive_type_array'] = 'any_of',
) -> dict[str, Any]
```

### Rebuild Schema

```python
@classmethod
def model_rebuild(
    cls,
    *,
    force: bool = False,
    raise_errors: bool = True,
    _parent_namespace_depth: int = 2,
    _types_namespace: MappingNamespace | None = None,
) -> bool | None
```

Rebuild model schema. Required when using forward references.

### Post-Init Hook

```python
def model_post_init(self, context: Any, /) -> None
```

Override to run logic after `__init__`. Called after all validation.

### Properties

```python
@property
def model_extra(self) -> dict[str, Any] | None    # Extra fields (extra='allow')

@property
def model_fields_set(self) -> set[str]             # Fields explicitly set at init
```

### Dynamic Model Creation

```python
def create_model(
    model_name: str, /,
    *,
    __config__: ConfigDict | None = None,
    __doc__: str | None = None,
    __base__: type[ModelT] | tuple[type[ModelT], ...] | None = None,
    __module__: str | None = None,
    __validators__: dict[str, Callable[..., Any]] | None = None,
    __cls_kwargs__: dict[str, Any] | None = None,
    __qualname__: str | None = None,
    **field_definitions: Any | tuple[Any, Any],
) -> type[ModelT]
```

Example:

```python
from pydantic import create_model

DynamicModel = create_model(
    'DynamicModel',
    name=(str, ...),           # required field
    age=(int, 25),             # field with default
    email=(str | None, None),  # optional field
)
```

---

## Fields

### Field() Function

Customize field behavior. Use in `Annotated` (recommended) or as default value.

```python
from pydantic import BaseModel, Field
from typing import Annotated

class User(BaseModel):
    # Annotated pattern (recommended for reusability)
    name: Annotated[str, Field(min_length=1, max_length=100)]
    # Direct assignment pattern
    age: int = Field(ge=0, le=150, description="User's age")
```

Full signature:

```python
def Field(
    default: Any = PydanticUndefined,
    *,
    default_factory: Callable[[], Any] | Callable[[dict[str, Any]], Any] | None = _Unset,
    alias: str | None = _Unset,
    alias_priority: int | None = _Unset,
    validation_alias: str | AliasPath | AliasChoices | None = _Unset,
    serialization_alias: str | None = _Unset,
    title: str | None = _Unset,
    field_title_generator: Callable[[str, FieldInfo], str] | None = _Unset,
    description: str | None = _Unset,
    examples: list[Any] | None = _Unset,
    exclude: bool | None = _Unset,
    exclude_if: Callable[[Any], bool] | None = _Unset,
    discriminator: str | Discriminator | None = _Unset,
    deprecated: Deprecated | str | bool | None = _Unset,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = _Unset,
    frozen: bool | None = _Unset,
    validate_default: bool | None = _Unset,
    repr: bool = _Unset,
    init: bool | None = _Unset,
    init_var: bool | None = _Unset,
    kw_only: bool | None = _Unset,
    pattern: str | re.Pattern[str] | None = _Unset,
    strict: bool | None = _Unset,
    coerce_numbers_to_str: bool | None = _Unset,
    gt: SupportsGt | None = _Unset,
    ge: SupportsGe | None = _Unset,
    lt: SupportsLt | None = _Unset,
    le: SupportsLe | None = _Unset,
    multiple_of: float | None = _Unset,
    allow_inf_nan: bool | None = _Unset,
    max_digits: int | None = _Unset,
    decimal_places: int | None = _Unset,
    min_length: int | None = _Unset,
    max_length: int | None = _Unset,
    union_mode: Literal['smart', 'left_to_right'] = _Unset,
    fail_fast: bool | None = _Unset,
) -> Any
```

### Field Parameter Reference

| Parameter | Type | Description |
|-----------|------|-------------|
| `default` | `Any` | Default value |
| `default_factory` | `Callable` | Factory for mutable defaults. Can accept `dict[str, Any]` of already-validated data |
| `alias` | `str` | Alias for both validation and serialization |
| `validation_alias` | `str \| AliasPath \| AliasChoices` | Alias for validation only |
| `serialization_alias` | `str` | Alias for serialization only |
| `title` | `str` | Human-readable title for JSON schema |
| `description` | `str` | Description for JSON schema |
| `examples` | `list[Any]` | Example values for JSON schema |
| `exclude` | `bool` | Exclude from serialization |
| `exclude_if` | `Callable[[Any], bool]` | Conditionally exclude from serialization |
| `discriminator` | `str \| Discriminator` | For discriminated unions |
| `deprecated` | `str \| bool` | Mark field as deprecated |
| `json_schema_extra` | `dict \| Callable` | Extra JSON schema properties |
| `frozen` | `bool` | Immutable field |
| `validate_default` | `bool` | Validate default values |
| `repr` | `bool` | Include in model repr |
| `strict` | `bool` | Strict type checking (no coercion) |
| `gt`, `ge`, `lt`, `le` | numeric | Numeric constraints |
| `min_length`, `max_length` | `int` | Length constraints |
| `pattern` | `str \| Pattern` | Regex pattern for strings |
| `multiple_of` | `float` | Numeric multiple constraint |
| `max_digits`, `decimal_places` | `int` | Decimal constraints |
| `union_mode` | `'smart' \| 'left_to_right'` | Union validation strategy |
| `fail_fast` | `bool` | Stop sequence validation on first error |

### FieldInfo Class

```python
class FieldInfo:
    annotation: type[Any] | None
    default: Any
    default_factory: Callable | None
    alias: str | None
    alias_priority: int | None
    validation_alias: str | AliasPath | AliasChoices | None
    serialization_alias: str | None
    title: str | None
    description: str | None
    examples: list[Any] | None
    exclude: bool | None
    exclude_if: Callable[[Any], bool] | None
    discriminator: str | Discriminator | None
    deprecated: Deprecated | str | bool | None
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None
    frozen: bool | None
    validate_default: bool | None
    repr: bool
    init: bool | None
    init_var: bool | None
    kw_only: bool | None
    metadata: list[Any]

    def is_required(self) -> bool: ...
    def get_default(self, *, call_default_factory: bool = False) -> Any: ...

    @classmethod
    def from_field(cls, default: Any = PydanticUndefined, **kwargs) -> FieldInfo: ...
    @classmethod
    def from_annotation(cls, annotation: type[Any]) -> FieldInfo: ...
    @classmethod
    def from_annotated_attribute(cls, annotation: type[Any], default: Any) -> FieldInfo: ...
```

### Private Attributes

```python
from pydantic import BaseModel, PrivateAttr

class Model(BaseModel):
    _secret: str = PrivateAttr(default='hidden')
    _computed: list[int] = PrivateAttr(default_factory=list)
```

```python
def PrivateAttr(
    default: Any = PydanticUndefined,
    *,
    default_factory: Callable[[], Any] | None = None,
) -> Any
```

Private attributes are **not** included in validation, serialization, or JSON schema. Access them as regular attributes after construction.

### Computed Fields

```python
from pydantic import BaseModel, computed_field

class Rectangle(BaseModel):
    width: float
    height: float

    @computed_field
    @property
    def area(self) -> float:
        return self.width * self.height
```

Full decorator signature:

```python
def computed_field(
    func: PropertyT | None = None, /,
    *,
    alias: str | None = None,
    alias_priority: int | None = None,
    exclude_if: Callable[[Any], bool] | None = None,
    title: str | None = None,
    field_title_generator: Callable[[str, ComputedFieldInfo], str] | None = None,
    description: str | None = None,
    deprecated: Deprecated | str | bool | None = None,
    examples: list[Any] | None = None,
    json_schema_extra: JsonDict | Callable[[JsonDict], None] | None = None,
    repr: bool | None = None,
    return_type: Any = PydanticUndefined,
) -> PropertyT | Callable[[PropertyT], PropertyT]
```

Computed fields are included in `model_dump()`, `model_dump_json()`, and JSON schema but are **read-only**.

---

## Validators

### Field Validators (Decorator Pattern)

Four modes: `after` (default), `before`, `wrap`, `plain`.

```python
from pydantic import BaseModel, field_validator

class User(BaseModel):
    name: str
    age: int

    # After validator (default): runs after Pydantic's built-in validation
    @field_validator('name')
    @classmethod
    def name_must_not_be_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('Name cannot be empty')
        return v.strip()

    # Before validator: runs before type coercion
    @field_validator('age', mode='before')
    @classmethod
    def parse_age(cls, v: Any) -> Any:
        if isinstance(v, str) and v.endswith('y'):
            return int(v[:-1])
        return v

    # Wrap validator: full control, wraps the handler
    @field_validator('name', mode='wrap')
    @classmethod
    def wrap_name(cls, v: Any, handler: ValidatorFunctionWrapHandler) -> str:
        result = handler(v)
        return result.title()
```

Full signature:

```python
def field_validator(
    field: str, /, *fields: str,
    mode: Literal['before', 'after', 'wrap', 'plain'] = 'after',
    check_fields: bool | None = None,
    json_schema_input_type: Any = PydanticUndefined,
) -> Callable
```

### Field Validators (Annotated Pattern)

Reusable validators via `Annotated`:

```python
from typing import Annotated
from pydantic import BaseModel
from pydantic.functional_validators import AfterValidator, BeforeValidator, WrapValidator, PlainValidator

def must_be_positive(v: int) -> int:
    if v <= 0:
        raise ValueError('Must be positive')
    return v

PositiveInt = Annotated[int, AfterValidator(must_be_positive)]

class Model(BaseModel):
    count: PositiveInt
```

```python
# AfterValidator: runs after Pydantic validation, receives validated type
AfterValidator(func: NoInfoValidatorFunction | WithInfoValidatorFunction)

# BeforeValidator: runs before Pydantic validation, receives raw input
BeforeValidator(func: ..., json_schema_input_type: Any = PydanticUndefined)

# PlainValidator: replaces Pydantic validation entirely
PlainValidator(func: ..., json_schema_input_type: Any = Any)

# WrapValidator: wraps Pydantic validation with handler
WrapValidator(func: ..., json_schema_input_type: Any = PydanticUndefined)
```

### Model Validators

Validate the entire model (all fields together).

```python
from pydantic import BaseModel, model_validator

class UserModel(BaseModel):
    username: str
    password: str
    password_confirm: str

    # After mode: receives model instance
    @model_validator(mode='after')
    def passwords_match(self) -> Self:
        if self.password != self.password_confirm:
            raise ValueError('Passwords do not match')
        return self

    # Before mode: receives raw input dict
    @model_validator(mode='before')
    @classmethod
    def preprocess(cls, data: Any) -> Any:
        if isinstance(data, str):
            return {'username': data, 'password': '', 'password_confirm': ''}
        return data

    # Wrap mode: full control
    @model_validator(mode='wrap')
    @classmethod
    def wrap_validate(cls, values: Any, handler: ModelWrapValidatorHandler) -> Self:
        instance = handler(values)
        return instance
```

```python
def model_validator(
    *,
    mode: Literal['wrap', 'before', 'after'],
) -> Callable
```

### Validation Info

Validators can receive `ValidationInfo` to access context and other validated data:

```python
from pydantic import BaseModel, field_validator, ValidationInfo

class Model(BaseModel):
    country: str
    city: str

    @field_validator('city')
    @classmethod
    def validate_city(cls, v: str, info: ValidationInfo) -> str:
        # info.data contains already-validated fields
        country = info.data.get('country')
        # info.context contains user-provided context
        # info.mode is 'python', 'json', or 'strings'
        # info.field_name is the current field name
        return v
```

### Validation Ordering

- **Before/wrap validators**: right-to-left (last defined runs first)
- **After validators**: left-to-right (first defined runs first)
- **Model validators**: same ordering rules

### Special Validator Types

```python
from pydantic.functional_validators import InstanceOf, SkipValidation, ValidateAs

# InstanceOf: only checks isinstance, no coercion
name: InstanceOf[str]

# SkipValidation: skip all validation for this field
data: SkipValidation[dict]

# ValidateAs: validate as one type, then transform
field: Annotated[TargetType, ValidateAs(SourceType, transform_func)]
```

---

## Serializers

### Field Serializers (Decorator Pattern)

```python
from pydantic import BaseModel, field_serializer

class Model(BaseModel):
    dt: datetime
    password: str

    # Plain mode (default): replaces default serialization
    @field_serializer('dt')
    def serialize_dt(self, dt: datetime) -> str:
        return dt.strftime('%Y-%m-%d')

    # Wrap mode: wraps default serialization
    @field_serializer('password', mode='wrap')
    def mask_password(self, v: str, handler: SerializerFunctionWrapHandler) -> str:
        return '***'
```

```python
def field_serializer(
    field: str, /, *fields: str,
    mode: Literal['plain', 'wrap'] = 'plain',
    return_type: Any = PydanticUndefined,
    when_used: Literal['always', 'unless-none', 'json', 'json-unless-none'] = 'always',
    check_fields: bool | None = None,
) -> Callable
```

### Field Serializers (Annotated Pattern)

```python
from pydantic.functional_serializers import PlainSerializer, WrapSerializer

# PlainSerializer: replaces default serialization
DoubleInt = Annotated[int, PlainSerializer(lambda v: v * 2)]

# WrapSerializer: wraps default serialization
def add_one(v: Any, handler: SerializerFunctionWrapHandler) -> int:
    return handler(v) + 1
IncrementedInt = Annotated[int, WrapSerializer(add_one)]
```

```python
PlainSerializer(
    func: SerializerFunction,
    return_type: Any = PydanticUndefined,
    when_used: Literal['always', 'unless-none', 'json', 'json-unless-none'] = 'always',
)

WrapSerializer(
    func: WrapSerializerFunction,
    return_type: Any = PydanticUndefined,
    when_used: Literal['always', 'unless-none', 'json', 'json-unless-none'] = 'always',
)
```

### Model Serializers

```python
from pydantic import BaseModel, model_serializer

class Model(BaseModel):
    name: str
    password: str

    # Plain model serializer: full custom output
    @model_serializer(mode='plain')
    def serialize(self) -> dict:
        return {'name': self.name}  # omit password

    # Wrap model serializer: modify default output
    @model_serializer(mode='wrap')
    def serialize(self, handler: SerializerFunctionWrapHandler) -> dict:
        data = handler(self)
        data['extra_key'] = 'value'
        return data
```

```python
def model_serializer(
    f: Callable | None = None, /,
    *,
    mode: Literal['plain', 'wrap'] = 'plain',
    when_used: Literal['always', 'unless-none', 'json', 'json-unless-none'] = 'always',
    return_type: Any = PydanticUndefined,
) -> Callable
```

### SerializeAsAny

Force serialization using the runtime type instead of the declared type:

```python
from pydantic import BaseModel, SerializeAsAny

class Animal(BaseModel):
    name: str

class Dog(Animal):
    breed: str

class Owner(BaseModel):
    pet: SerializeAsAny[Animal]  # Will serialize breed if runtime type is Dog
```

### Serialization Features

```python
# Exclude/include fields
model.model_dump(exclude={'password'})
model.model_dump(include={'id', 'name'})

# Nested exclude
model.model_dump(exclude={'user': {'password'}})

# Exclude by state
model.model_dump(exclude_unset=True)      # Skip fields not explicitly set
model.model_dump(exclude_defaults=True)    # Skip fields with default values
model.model_dump(exclude_none=True)        # Skip None fields

# Use aliases
model.model_dump(by_alias=True)

# Polymorphic serialization (serialize subclass fields)
model.model_dump(polymorphic_serialization=True)

# Pass context to serializers
model.model_dump(context={'include_sensitive': False})
```

---

## Configuration (ConfigDict)

Configure model behavior via `model_config`:

```python
from pydantic import BaseModel, ConfigDict

class Model(BaseModel):
    model_config = ConfigDict(
        strict=True,
        frozen=True,
        extra='forbid',
    )
    name: str
```

### Complete ConfigDict Reference

```python
class ConfigDict(TypedDict, total=False):
    # --- Title & Documentation ---
    title: str | None                                                    # Model title for JSON schema
    model_title_generator: Callable[[type], str] | None                  # Generate model titles programmatically
    field_title_generator: Callable[[str, FieldInfo | ComputedFieldInfo], str] | None

    # --- String Handling ---
    str_to_lower: bool                     # Convert strings to lowercase (default: False)
    str_to_upper: bool                     # Convert strings to uppercase (default: False)
    str_strip_whitespace: bool             # Strip whitespace from strings (default: False)
    str_min_length: int                    # Global minimum string length (default: 0)
    str_max_length: int | None             # Global maximum string length (default: None)

    # --- Extra Fields ---
    extra: Literal['allow', 'ignore', 'forbid'] | None  # How to handle extra fields (default: 'ignore')

    # --- Immutability ---
    frozen: bool                           # Make model immutable (default: False)

    # --- Field Name Handling ---
    populate_by_name: bool                 # DEPRECATED: use validate_by_name instead
    validate_by_alias: bool                # Allow validation by alias (default: True)
    validate_by_name: bool                 # Allow validation by field name (default: True when no alias, else False)
    serialize_by_alias: bool               # Serialize using alias by default (default: False)

    # --- Enum Handling ---
    use_enum_values: bool                  # Use enum .value instead of enum instance (default: False)

    # --- Assignment Validation ---
    validate_assignment: bool              # Validate on attribute assignment (default: False)

    # --- Arbitrary Types ---
    arbitrary_types_allowed: bool          # Allow types without pydantic schema (default: False)

    # --- ORM Mode ---
    from_attributes: bool                  # Extract data from object attributes (default: False)

    # --- Error Formatting ---
    loc_by_alias: bool                     # Use alias in error locations (default: True)

    # --- Alias Generation ---
    alias_generator: Callable[[str], str] | AliasGenerator | None  # Generate aliases (default: None)

    # --- Type Ignoring ---
    ignored_types: tuple[type, ...]        # Types to ignore during model creation

    # --- Numeric ---
    allow_inf_nan: bool                    # Allow inf/nan in floats (default: True)
    coerce_numbers_to_str: bool            # Coerce numbers to strings (default: False)

    # --- JSON Schema ---
    json_schema_extra: JsonDict | Callable | None     # Extra JSON schema properties
    json_schema_serialization_defaults_required: bool  # Mark fields with defaults as required in serialization schema
    json_schema_mode_override: Literal['validation', 'serialization'] | None

    # --- Strict Mode ---
    strict: bool                           # Disable type coercion (default: False)

    # --- Revalidation ---
    revalidate_instances: Literal['always', 'never', 'subclass-instances']  # (default: 'never')

    # --- JSON Serialization Options ---
    ser_json_timedelta: Literal['iso8601', 'float']               # (default: 'iso8601')
    ser_json_temporal: Literal['iso8601', 'seconds', 'milliseconds']  # (default: 'iso8601')
    ser_json_bytes: Literal['utf8', 'base64', 'hex']              # (default: 'utf8')
    ser_json_inf_nan: Literal['null', 'constants', 'strings']     # (default: 'null')
    val_json_bytes: Literal['utf8', 'base64', 'hex']              # (default: 'utf8')
    val_temporal_unit: Literal['seconds', 'milliseconds', 'infer']  # (default: 'infer')

    # --- Validation Options ---
    validate_default: bool                 # Validate default values (default: False)
    validate_return: bool                  # Validate return types in validate_call (default: False)
    protected_namespaces: tuple[str | Pattern[str], ...]  # Protected attribute prefixes (default: ('model_',))
    hide_input_in_errors: bool             # Hide input values in errors (default: False)
    validation_error_cause: bool           # Include cause in ValidationError (default: False)

    # --- Build Options ---
    defer_build: bool                      # Defer schema building until first use (default: False)
    plugin_settings: dict[str, object] | None  # Plugin configuration
    schema_generator: type | None          # Custom schema generator class

    # --- Regex ---
    regex_engine: Literal['rust-regex', 'python-re']  # (default: 'rust-regex')

    # --- Documentation ---
    use_attribute_docstrings: bool         # Use field docstrings as descriptions (default: False)

    # --- String Caching ---
    cache_strings: bool | Literal['all', 'keys', 'none']  # Cache strings during validation

    # --- URL ---
    url_preserve_empty_path: bool          # Preserve empty URL paths (default: False)

    # --- Polymorphism ---
    polymorphic_serialization: bool        # Serialize subclass types with all fields (default: False)
```

### with_config Decorator

Apply config to TypedDicts, dataclasses, or other types:

```python
from pydantic import with_config, ConfigDict

@with_config(ConfigDict(strict=True))
class MyTypedDict(TypedDict):
    name: str
```

---

## Types

### Constrained Types

```python
from pydantic import (
    conint, confloat, constr, conbytes,
    conlist, conset, confrozenset,
    condecimal, condate,
)
```

```python
conint(*, strict=None, gt=None, ge=None, lt=None, le=None, multiple_of=None) -> type[int]
confloat(*, strict=None, gt=None, ge=None, lt=None, le=None, multiple_of=None, allow_inf_nan=None) -> type[float]
constr(*, strip_whitespace=None, to_upper=None, to_lower=None, strict=None, min_length=None, max_length=None, pattern=None, ascii_only=None) -> type[str]
conbytes(*, min_length=None, max_length=None, strict=None) -> type[bytes]
conlist(item_type, *, min_length=None, max_length=None) -> type[list]
conset(item_type, *, min_length=None, max_length=None) -> type[set]
confrozenset(item_type, *, min_length=None, max_length=None) -> type[frozenset]
condecimal(*, strict=None, gt=None, ge=None, lt=None, le=None, multiple_of=None, max_digits=None, decimal_places=None, allow_inf_nan=None) -> type[Decimal]
condate(*, strict=None, gt=None, ge=None, lt=None, le=None) -> type[date]
```

### Strict Types (No Coercion)

```python
from pydantic import StrictBool, StrictInt, StrictFloat, StrictStr, StrictBytes
```

These are equivalent to `Annotated[type, Strict()]`.

### Numeric Types

```python
from pydantic import (
    PositiveInt,      # Annotated[int, Gt(0)]
    NegativeInt,      # Annotated[int, Lt(0)]
    NonNegativeInt,   # Annotated[int, Ge(0)]
    NonPositiveInt,   # Annotated[int, Le(0)]
    PositiveFloat,    # Annotated[float, Gt(0)]
    NegativeFloat,    # Annotated[float, Lt(0)]
    NonNegativeFloat, # Annotated[float, Ge(0)]
    NonPositiveFloat, # Annotated[float, Le(0)]
    FiniteFloat,      # float excluding inf/nan
)
```

### String Constraints

```python
from pydantic import StringConstraints

class Model(BaseModel):
    name: Annotated[str, StringConstraints(
        strip_whitespace=True,
        to_upper=False,
        to_lower=False,
        strict=False,
        min_length=1,
        max_length=100,
        pattern=r'^[a-zA-Z]+$',
        ascii_only=False,
    )]
```

### UUID Types

```python
from pydantic import UUID1, UUID3, UUID4, UUID5, UUID6, UUID7, UUID8
```

Each validates that the UUID is of the specified version.

### Path Types

```python
from pydantic import FilePath, DirectoryPath, NewPath, SocketPath

class Config(BaseModel):
    input_file: FilePath          # Must exist and be a file
    output_dir: DirectoryPath     # Must exist and be a directory
    log_path: NewPath             # Must NOT exist (for creating new files)
    sock: SocketPath              # Must be a Unix socket
```

### Secret Types

```python
from pydantic import SecretStr, SecretBytes, Secret

class Config(BaseModel):
    password: SecretStr
    api_key: SecretBytes
    token: Secret[str]           # Generic secret type

config = Config(password='s3cret', api_key=b'key', token='tok')
print(config.password)                    # SecretStr('**********')
print(config.password.get_secret_value()) # 's3cret'
```

Secret types display `'**********'` in `__repr__` and `__str__` to prevent accidental logging.

### Encoded Types

```python
from pydantic import Base64Bytes, Base64Str, Base64UrlBytes, Base64UrlStr

class Model(BaseModel):
    data: Base64Bytes     # Accepts base64 string, stores as bytes
    text: Base64Str       # Accepts base64 string, stores as str
```

### Special Types

```python
from pydantic import Json, ImportString, PaymentCardNumber, ByteSize

class Model(BaseModel):
    # Json: accepts JSON string, validates inner type
    metadata: Json[dict[str, Any]]    # '{"key": "val"}' -> {'key': 'val'}

    # ImportString: dotted import path resolved to Python object
    handler: ImportString              # 'math.sqrt' -> <function sqrt>

    # PaymentCardNumber: validates Luhn algorithm
    card: PaymentCardNumber

    # ByteSize: human-readable byte sizes
    max_size: ByteSize                 # '1.5GB' -> 1500000000
```

ByteSize methods:
```python
size = ByteSize(1_500_000_000)
size.human_readable()                  # '1.4GiB'
size.human_readable(decimal=True)      # '1.5GB'
size.to('MB')                          # 1500.0
```

### Temporal Types

```python
from pydantic import (
    PastDate,          # date in the past
    FutureDate,        # date in the future
    PastDatetime,      # datetime in the past
    FutureDatetime,    # datetime in the future
    AwareDatetime,     # datetime with timezone info
    NaiveDatetime,     # datetime without timezone info
)
```

### Schema Metadata Types

```python
from pydantic import (
    GetPydanticSchema,   # Custom schema provider
    Discriminator,       # Union discriminator
    Tag,                 # Field tagging for unions
    JsonValue,           # Type alias for valid JSON values
    OnErrorOmit,         # Omit item from list on validation error
    FailFast,            # Stop sequence validation on first error
    AllowInfNan,         # Allow infinity/NaN in float fields
)
```

### Custom Types via `__get_pydantic_core_schema__`

```python
from pydantic import GetCoreSchemaHandler
from pydantic_core import core_schema

class CustomType:
    def __init__(self, value: str):
        self.value = value

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: Any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        return core_schema.no_info_plain_validator_function(
            cls._validate,
            serialization=core_schema.plain_serializer_function_ser_schema(
                cls._serialize, info_arg=False
            ),
        )

    @classmethod
    def _validate(cls, value: Any) -> 'CustomType':
        if isinstance(value, str):
            return cls(value)
        raise ValueError('Expected string')

    def _serialize(self) -> str:
        return self.value
```

---

## Network Types

```python
from pydantic import (
    # URLs
    AnyUrl,           # Any URL scheme
    AnyHttpUrl,       # http or https
    HttpUrl,          # http or https, max length 2083
    AnyWebsocketUrl,  # ws or wss
    WebsocketUrl,     # ws or wss, max length 2083
    FileUrl,          # file://
    FtpUrl,           # ftp://

    # DSNs (Database Connection Strings)
    PostgresDsn,      # postgres://, postgresql://, etc.
    CockroachDsn,     # cockroachdb://
    AmqpDsn,          # amqp://, amqps://
    RedisDsn,         # redis://, rediss://
    MongoDsn,         # mongodb://, mongodb+srv://
    KafkaDsn,         # kafka://
    NatsDsn,          # nats://, tls://, ws://
    MySQLDsn,         # mysql://, mysql+*://
    MariaDBDsn,       # mariadb://, mariadb+*://
    ClickHouseDsn,    # clickhouse+*://
    SnowflakeDsn,     # snowflake://

    # Email
    EmailStr,         # Validated email string (requires email-validator)
    NameEmail,        # "Name <email>" format

    # IP
    IPvAnyAddress,    # IPv4Address | IPv6Address
    IPvAnyInterface,  # IPv4Interface | IPv6Interface
    IPvAnyNetwork,    # IPv4Network | IPv6Network
)
```

### URL Class Methods & Properties

```python
url = HttpUrl('https://user:pass@example.com:8080/path?q=1#frag')

url.scheme        # 'https'
url.username      # 'user'
url.password      # 'pass'
url.host          # 'example.com'
url.port          # 8080
url.path          # '/path'
url.query         # 'q=1'
url.fragment      # 'frag'
url.unicode_host()    # Decoded IDN host
url.query_params()    # [('q', '1')]
url.unicode_string()  # Full URL as unicode
url.encoded_string()  # Full URL as encoded string

# Build URL programmatically
url = HttpUrl.build(
    scheme='https',
    host='example.com',
    port=8080,
    path='/api/v1',
    query='key=value',
)
```

### URL Constraints

```python
from pydantic import UrlConstraints

MyUrl = Annotated[AnyUrl, UrlConstraints(
    max_length=500,
    allowed_schemes=['https'],
    host_required=True,
    default_host='localhost',
    default_port=443,
    default_path='/api',
)]
```

### NameEmail

```python
from pydantic import NameEmail

class Contact(BaseModel):
    email: NameEmail

c = Contact(email='John Doe <john@example.com>')
c.email.name   # 'John Doe'
c.email.email  # 'john@example.com'
str(c.email)   # 'John Doe <john@example.com>'
```

---

## JSON Schema

### Generate Schema

```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int

# From model class
schema = User.model_json_schema()

# From model with mode
schema = User.model_json_schema(mode='serialization')
```

### Multi-Model Schema

```python
from pydantic.json_schema import models_json_schema

schemas, top_level = models_json_schema(
    [(User, 'validation'), (User, 'serialization')],
    title='My API',
    description='API schema',
)
```

### Customize JSON Schema

```python
from pydantic.json_schema import WithJsonSchema, SkipJsonSchema, Examples

class Model(BaseModel):
    # Override JSON schema for a field
    data: Annotated[CustomType, WithJsonSchema({'type': 'string', 'format': 'custom'})]

    # Exclude from JSON schema
    internal: SkipJsonSchema[int]

    # Add examples
    name: Annotated[str, Examples(['Alice', 'Bob'])]
```

### Custom Schema Generator

```python
from pydantic.json_schema import GenerateJsonSchema

class MyGenerator(GenerateJsonSchema):
    def generate(self, schema, mode='validation'):
        json_schema = super().generate(schema, mode=mode)
        json_schema['$id'] = 'my-custom-id'
        return json_schema

schema = Model.model_json_schema(schema_generator=MyGenerator)
```

### GenerateJsonSchema Class

```python
class GenerateJsonSchema:
    schema_dialect: str = 'https://json-schema.org/draft/2020-12/schema'
    ignored_warning_kinds: set[JsonSchemaWarningKind] = {'skipped-choice'}

    def __init__(
        self,
        by_alias: bool = True,
        ref_template: str = '#/$defs/{model}',
        union_format: Literal['any_of', 'primitive_type_array'] = 'any_of',
    ): ...

    def generate(self, schema: CoreSchema, mode: JsonSchemaMode = 'validation') -> JsonSchemaValue: ...
    def generate_definitions(self, inputs: Sequence[...]) -> tuple[dict, dict]: ...
```

---

## TypeAdapter

Validate and serialize **any type**, not just BaseModel subclasses.

```python
from pydantic import TypeAdapter

# Validate a list of ints
adapter = TypeAdapter(list[int])
result = adapter.validate_python(['1', '2', '3'])  # [1, 2, 3]

# Validate JSON
result = adapter.validate_json(b'[1, 2, 3]')

# Serialize
adapter.dump_python([1, 2, 3])       # [1, 2, 3]
adapter.dump_json([1, 2, 3])         # b'[1,2,3]'

# JSON schema
adapter.json_schema()
```

### Full Constructor

```python
class TypeAdapter(Generic[T]):
    def __init__(
        self,
        type: Any,
        *,
        config: ConfigDict | None = None,
        module: str | None = None,
    ) -> None: ...
```

### Methods

```python
def validate_python(
    self, object: Any, /,
    *,
    strict: bool | None = None,
    extra: ExtraValues | None = None,
    from_attributes: bool | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> T: ...

def validate_json(
    self, data: str | bytes | bytearray, /,
    *,
    strict: bool | None = None,
    extra: ExtraValues | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> T: ...

def validate_strings(
    self, obj: Any, /,
    *,
    strict: bool | None = None,
    extra: ExtraValues | None = None,
    context: Any | None = None,
    by_alias: bool | None = None,
    by_name: bool | None = None,
) -> T: ...

def dump_python(
    self, instance: T, /,
    *,
    mode: Literal['json', 'python'] = 'python',
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    exclude_computed_fields: bool = False,
    round_trip: bool = False,
    warnings: bool | Literal['none', 'warn', 'error'] = True,
    fallback: Callable[[Any], Any] | None = None,
    serialize_as_any: bool = False,
    context: Any | None = None,
) -> Any: ...

def dump_json(
    self, instance: T, /,
    *,
    indent: int | None = None,
    ensure_ascii: bool = False,
    include: IncEx | None = None,
    exclude: IncEx | None = None,
    by_alias: bool | None = None,
    exclude_unset: bool = False,
    exclude_defaults: bool = False,
    exclude_none: bool = False,
    exclude_computed_fields: bool = False,
    round_trip: bool = False,
    warnings: bool | Literal['none', 'warn', 'error'] = True,
    fallback: Callable[[Any], Any] | None = None,
    serialize_as_any: bool = False,
    context: Any | None = None,
) -> bytes: ...

def json_schema(
    self,
    *,
    by_alias: bool = True,
    ref_template: str = '#/$defs/{model}',
    union_format: Literal['any_of', 'primitive_type_array'] = 'any_of',
    schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
    mode: Literal['validation', 'serialization'] = 'validation',
) -> dict[str, Any]: ...

@staticmethod
def json_schemas(
    inputs: Iterable[tuple[JsonSchemaKeyT, JsonSchemaMode, TypeAdapter[Any]]], /,
    *,
    by_alias: bool = True,
    title: str | None = None,
    description: str | None = None,
    ref_template: str = '#/$defs/{model}',
    union_format: Literal['any_of', 'primitive_type_array'] = 'any_of',
    schema_generator: type[GenerateJsonSchema] = GenerateJsonSchema,
) -> tuple[dict, JsonSchemaValue]: ...

def get_default_value(
    self,
    *,
    strict: bool | None = None,
    context: Any | None = None,
) -> Some[T] | None: ...

def rebuild(
    self,
    *,
    force: bool = False,
    raise_errors: bool = True,
    _types_namespace: MappingNamespace | None = None,
) -> bool | None: ...
```

**Performance note**: Create `TypeAdapter` instances once and reuse them. Do not recreate in loops.

---

## RootModel

A model with a single root value (no named fields).

```python
from pydantic import RootModel

class Tags(RootModel[list[str]]):
    pass

tags = Tags(['python', 'pydantic'])
tags.root          # ['python', 'pydantic']
tags.model_dump()  # ['python', 'pydantic']  (returns root directly, not a dict)
```

### Class Signature

```python
class RootModel(BaseModel, Generic[RootModelRootType]):
    root: RootModelRootType

    def __init__(self, /, root: RootModelRootType = PydanticUndefined, **data) -> None: ...

    @classmethod
    def model_construct(cls, root: RootModelRootType, _fields_set: set[str] | None = None) -> Self: ...

    def model_dump(self, **kwargs) -> Any: ...  # Returns root value, not dict
```

### Use Cases

```python
# Validated list
class UserList(RootModel[list[User]]):
    pass

# Validated dict
class UserMap(RootModel[dict[str, User]]):
    pass

# Validated union
class Response(RootModel[SuccessResponse | ErrorResponse]):
    pass
```

---

## Dataclasses

Pydantic-enhanced dataclasses with validation.

```python
from pydantic.dataclasses import dataclass
from pydantic import ConfigDict

@dataclass(config=ConfigDict(strict=True))
class User:
    name: str
    age: int
    email: str | None = None
```

### Decorator Signature

```python
def dataclass(
    _cls: type[_T] | None = None,
    *,
    init: Literal[False] = False,
    repr: bool = True,
    eq: bool = True,
    order: bool = False,
    unsafe_hash: bool = False,
    frozen: bool | None = None,
    config: ConfigDict | type[object] | None = None,
    validate_on_init: bool | None = None,
    kw_only: bool = False,
    slots: bool = False,
) -> type[PydanticDataclass]
```

### Key Differences from BaseModel

- No `model_dump()`, `model_validate()`, etc. Use `TypeAdapter` wrapper:
  ```python
  adapter = TypeAdapter(User)
  adapter.validate_python({'name': 'Alice', 'age': 30})
  adapter.dump_python(user)
  ```
- `__post_init__()` runs between before and after validators
- Extra fields not included in serialization
- No `model_config` attribute (use `config=` parameter)

### Utility Functions

```python
from pydantic.dataclasses import rebuild_dataclass, is_pydantic_dataclass

rebuild_dataclass(cls, *, force=False, raise_errors=True) -> bool | None
is_pydantic_dataclass(class_: type) -> TypeGuard[type[PydanticDataclass]]
```

---

## Aliases

### Alias Types

```python
from pydantic import AliasPath, AliasChoices, AliasGenerator

# Simple alias
class Model(BaseModel):
    name: str = Field(alias='userName')

# Validation-only alias (input)
class Model(BaseModel):
    name: str = Field(validation_alias='user_name')

# Serialization-only alias (output)
class Model(BaseModel):
    name: str = Field(serialization_alias='userName')
```

### AliasPath - Nested Access

```python
class User(BaseModel):
    first_name: str = Field(validation_alias=AliasPath('names', 0))
    city: str = Field(validation_alias=AliasPath('address', 'city'))

user = User.model_validate({
    'names': ['Alice', 'Smith'],
    'address': {'city': 'NYC'}
})
```

```python
class AliasPath:
    def __init__(self, first_arg: str, *args: str | int) -> None: ...
    def convert_to_aliases(self) -> list[str | int]: ...
```

### AliasChoices - Multiple Options

```python
class User(BaseModel):
    name: str = Field(validation_alias=AliasChoices('name', 'username', 'user_name'))

# Can combine with AliasPath
class User(BaseModel):
    name: str = Field(
        validation_alias=AliasChoices('name', AliasPath('user', 'name'))
    )
```

```python
class AliasChoices:
    def __init__(self, first_choice: str | AliasPath, *choices: str | AliasPath) -> None: ...
    def convert_to_aliases(self) -> list[list[str | int]]: ...
```

### AliasGenerator

```python
class AliasGenerator:
    alias: Callable[[str], str] | None = None
    validation_alias: Callable[[str], str | AliasPath | AliasChoices] | None = None
    serialization_alias: Callable[[str], str] | None = None
```

Usage:

```python
from pydantic import ConfigDict, AliasGenerator
from pydantic.alias_generators import to_camel, to_pascal, to_snake

class Model(BaseModel):
    model_config = ConfigDict(
        alias_generator=AliasGenerator(
            validation_alias=to_camel,
            serialization_alias=to_pascal,
        )
    )
    user_name: str
    email_address: str

# Validate with camelCase: {'userName': 'Alice', 'emailAddress': 'a@b.com'}
# Serialize with PascalCase: {'UserName': 'Alice', 'EmailAddress': 'a@b.com'}
```

### Built-in Alias Generators

```python
from pydantic.alias_generators import to_pascal, to_camel, to_snake

to_pascal('user_name')  # 'UserName'
to_camel('user_name')   # 'userName'
to_snake('UserName')    # 'user_name'
to_snake('camelCase')   # 'camel_case'
to_snake('kebab-case')  # 'kebab_case'
```

### Alias Priority

- `alias_priority=2`: Alias is NOT overridden by generator
- `alias_priority=1`: Alias IS overridden by generator
- Default when alias set explicitly: priority 2 (not overridden)
- Default when no alias: priority 0 (overridden by generator)

---

## validate_call

Validate function arguments and return values using Pydantic.

```python
from pydantic import validate_call

@validate_call
def greet(name: str, age: int) -> str:
    return f'Hello {name}, you are {age}'

greet('Alice', '30')  # Works: '30' coerced to int
greet('Alice', 'abc') # ValidationError
```

### Signature

```python
def validate_call(
    func: Callable | None = None, /,
    *,
    config: ConfigDict | None = None,
    validate_return: bool = False,
) -> Callable
```

### With Configuration

```python
@validate_call(config=ConfigDict(strict=True), validate_return=True)
def process(data: list[int]) -> int:
    return sum(data)
```

---

## Errors

### ValidationError

From `pydantic_core`. Raised when validation fails.

```python
from pydantic import BaseModel, ValidationError

try:
    User(name=123)
except ValidationError as e:
    e.errors()       # List of error dicts
    e.error_count()  # Number of errors
    e.json()         # JSON representation
    str(e)           # Human-readable string
```

Error dict structure:
```python
{
    'type': 'string_type',           # Error type code
    'loc': ('name',),                # Location tuple
    'msg': 'Input should be a valid string',
    'input': 123,                    # The invalid input
    'url': 'https://errors.pydantic.dev/...',
}
```

### Pydantic-Specific Errors

```python
from pydantic import (
    PydanticUserError,                # Incorrect use of Pydantic API
    PydanticSchemaGenerationError,    # Failed to generate CoreSchema
    PydanticInvalidForJsonSchema,     # Failed to generate JSON schema
    PydanticImportError,              # Import error (V1 -> V2 changes)
    PydanticUndefinedAnnotation,      # Undefined forward reference
    PydanticForbiddenQualifier,       # Forbidden type qualifier (e.g., ClassVar)
)
```

### Error Codes

`PydanticErrorCodes` is a `Literal` type with all valid error codes:

`'class-not-fully-defined'`, `'custom-json-schema'`, `'decorator-invalid-fields'`, `'decorator-missing-arguments'`, `'decorator-missing-field'`, `'discriminator-no-field'`, `'discriminator-alias-type'`, `'discriminator-needs-literal'`, `'discriminator-alias'`, `'discriminator-validator'`, `'callable-discriminator-no-tag'`, `'typed-dict-version'`, `'model-field-overridden'`, `'model-field-missing-annotation'`, `'config-both'`, `'removed-kwargs'`, `'circular-reference-schema'`, `'invalid-for-json-schema'`, `'json-schema-already-used'`, `'base-model-instantiated'`, `'undefined-annotation'`, `'schema-for-unknown-type'`, `'import-error'`, `'create-model-field-definitions'`, `'validator-instance-method'`, `'root-model-extra'`, `'unevaluable-type-annotation'`, `'dataclass-init-false-extra-allow'`, `'clashing-init-and-init-var'`, `'model-config-invalid-field-name'`, `'with-config-on-model'`, `'dataclass-on-model'`, `'validate-call-type'`

---

## Experimental: Pipeline API

```python
from pydantic.experimental.pipeline import validate_as, transform, validate_as_deferred
```

**Note**: Experimental API, may change.

### Basic Usage

```python
from typing import Annotated
from pydantic.experimental.pipeline import validate_as

# Validate with constraints
PositiveInt = Annotated[int, validate_as(int).gt(0)]

# Chain constraints
BoundedInt = Annotated[int, validate_as(int).ge(0).le(100)]

# Transform
LowerStr = Annotated[str, transform(str.strip).str_lower()]
```

### Available Constraint Methods

| Method | Description |
|--------|-------------|
| `.gt(value)` | Greater than |
| `.lt(value)` | Less than |
| `.ge(value)` | Greater than or equal |
| `.le(value)` | Less than or equal |
| `.eq(value)` | Equal to |
| `.not_eq(value)` | Not equal to |
| `.in_(collection)` | Value in collection |
| `.not_in(collection)` | Value not in collection |
| `.len(min, max)` | Length constraint |
| `.multiple_of(value)` | Multiple of value |
| `.predicate(func)` | Custom predicate function |

### String Methods

`.str_lower()`, `.str_upper()`, `.str_title()`, `.str_strip()`, `.str_pattern(regex)`, `.str_contains(s)`, `.str_starts_with(s)`, `.str_ends_with(s)`

### DateTime Methods

`.datetime_tz_naive()`, `.datetime_tz_aware()`, `.datetime_tz(tz)`, `.datetime_with_tz(tz)`

### Logical Operators

```python
# OR: try first, fallback to second
field: Annotated[int, validate_as(int).gt(0).otherwise(validate_as(str))]

# AND: pipe result
field: Annotated[str, validate_as(str).then(transform(str.lower))]
```

---

## Performance Tips

1. **Use `model_validate_json()` over `json.loads()` + `model_validate()`** — directly parsing JSON is faster.

2. **Create `TypeAdapter` once, reuse** — construction is expensive.

3. **Use specific types over abstract ones** — `list[int]` is faster than `Sequence[int]`.

4. **Use discriminated unions** — `Field(discriminator='type')` is much faster than smart union matching.

5. **Prefer `TypedDict` over nested `BaseModel`** — ~2.5x faster for nested structures when you don't need model methods.

6. **Avoid `Sequence`/`Mapping`** — use `list`/`dict` directly.

7. **Avoid wrap validators** — they require Python materialization. Use before/after when possible.

8. **Use `FailFast` for sequences** — stop validation on first error:
   ```python
   items: Annotated[list[int], FailFast()]
   ```

9. **Use `Any` type** to skip validation when data is already trusted.

10. **Avoid subclassing primitives** (`str`, `int`) for carrying extra data — use nested models instead.

---

## Strict Mode

Disables automatic type coercion. Values must match the exact declared type.

### Three Levels of Strictness

```python
# 1. Config-level (lowest priority)
class Model(BaseModel):
    model_config = ConfigDict(strict=True)
    value: int  # Only accepts int, not '123'

# 2. Field-level
class Model(BaseModel):
    strict_value: int = Field(strict=True)
    lax_value: int  # Still accepts '123'

# 3. Validation-level (highest priority)
Model.model_validate({'value': '123'}, strict=True)
```

### Convenience Type Aliases

```python
StrictBool    # Annotated[bool, Strict()]
StrictInt     # Annotated[int, Strict()]
StrictFloat   # Annotated[float, Strict()]
StrictStr     # Annotated[str, Strict()]
StrictBytes   # Annotated[bytes, Strict()]
```

### Strict Mode Behavior

- `int` accepts only `int` (not `float`, `str`, `bool`)
- `str` accepts only `str` (not `bytes`, `int`)
- `bool` accepts only `bool` (not `int`, `str`)
- `float` accepts only `float` or `int` (not `str`)
- JSON input is slightly more lenient (e.g., date fields accept ISO strings)

---

## Unions

### Smart Union (Default)

Pydantic attempts to find the best match:

```python
from pydantic import BaseModel

class Model(BaseModel):
    value: int | str  # Smart mode: prefers exact type match

Model(value=42)    # int match
Model(value='hi')  # str match
```

For models/dataclasses: ranks by number of valid fields. For primitives: prefers exact > strict > lax match.

### Left-to-Right Union

Try each member in order:

```python
class Model(BaseModel):
    value: int | str = Field(union_mode='left_to_right')

Model(value='42')  # Returns int(42) because int is tried first
```

### Discriminated Unions (Recommended)

Fastest and most predictable. Use a discriminator field:

```python
from pydantic import BaseModel, Field
from typing import Literal, Union

class Cat(BaseModel):
    pet_type: Literal['cat']
    name: str

class Dog(BaseModel):
    pet_type: Literal['dog']
    name: str
    breed: str

class Owner(BaseModel):
    pet: Union[Cat, Dog] = Field(discriminator='pet_type')

Owner(pet={'pet_type': 'cat', 'name': 'Whiskers'})  # Cat instance
Owner(pet={'pet_type': 'dog', 'name': 'Rex', 'breed': 'Lab'})  # Dog instance
```

### Callable Discriminator

```python
from pydantic import Discriminator, Tag
from typing import Annotated, Union

def get_pet_type(v: Any) -> str:
    if isinstance(v, dict):
        return v.get('type', 'unknown')
    return getattr(v, 'type', 'unknown')

class Owner(BaseModel):
    pet: Annotated[
        Union[
            Annotated[Cat, Tag('cat')],
            Annotated[Dog, Tag('dog')],
        ],
        Discriminator(get_pet_type),
    ]
```

### OnErrorOmit

Skip invalid items in sequences instead of raising errors:

```python
from pydantic import TypeAdapter, OnErrorOmit

adapter = TypeAdapter(list[OnErrorOmit[int]])
result = adapter.validate_python([1, 'not_int', 3])  # [1, 3]
```

---

## Full Import Reference

```python
# Core
from pydantic import BaseModel, RootModel, create_model

# Fields
from pydantic import Field, FieldInfo, PrivateAttr, computed_field

# Validators
from pydantic import field_validator, model_validator, ValidationInfo
from pydantic.functional_validators import (
    AfterValidator, BeforeValidator, PlainValidator, WrapValidator,
    InstanceOf, SkipValidation, ValidateAs, ModelWrapValidatorHandler,
)

# Serializers
from pydantic import field_serializer, model_serializer
from pydantic.functional_serializers import (
    PlainSerializer, WrapSerializer, SerializeAsAny,
)

# Configuration
from pydantic import ConfigDict, with_config

# Type Adapter
from pydantic import TypeAdapter

# Types - Numeric
from pydantic import (
    PositiveInt, NegativeInt, NonNegativeInt, NonPositiveInt,
    PositiveFloat, NegativeFloat, NonNegativeFloat, NonPositiveFloat,
    FiniteFloat, StrictInt, StrictFloat, StrictBool, StrictStr, StrictBytes,
)

# Types - Constrained
from pydantic import conint, confloat, constr, conbytes, conlist, conset, confrozenset, condecimal, condate
from pydantic import StringConstraints

# Types - Special
from pydantic import (
    Json, ImportString, PaymentCardNumber, ByteSize,
    Secret, SecretStr, SecretBytes,
    Base64Bytes, Base64Str, Base64UrlBytes, Base64UrlStr,
    EncodedBytes, EncodedStr,
)

# Types - Path
from pydantic import FilePath, DirectoryPath, NewPath, SocketPath

# Types - Temporal
from pydantic import PastDate, FutureDate, PastDatetime, FutureDatetime, AwareDatetime, NaiveDatetime

# Types - UUID
from pydantic import UUID1, UUID3, UUID4, UUID5, UUID6, UUID7, UUID8

# Types - Network
from pydantic import (
    AnyUrl, AnyHttpUrl, HttpUrl, WebsocketUrl, AnyWebsocketUrl, FileUrl, FtpUrl,
    PostgresDsn, CockroachDsn, AmqpDsn, RedisDsn, MongoDsn, KafkaDsn,
    NatsDsn, MySQLDsn, MariaDBDsn, ClickHouseDsn, SnowflakeDsn,
    EmailStr, NameEmail,
    IPvAnyAddress, IPvAnyInterface, IPvAnyNetwork,
    UrlConstraints,
)

# Types - Schema Metadata
from pydantic import (
    GetPydanticSchema, Discriminator, Tag, JsonValue,
    OnErrorOmit, FailFast, AllowInfNan,
)

# Aliases
from pydantic import AliasPath, AliasChoices, AliasGenerator
from pydantic.alias_generators import to_pascal, to_camel, to_snake

# JSON Schema
from pydantic.json_schema import GenerateJsonSchema, WithJsonSchema, SkipJsonSchema, Examples

# Decorator
from pydantic import validate_call

# Dataclasses
from pydantic.dataclasses import dataclass, rebuild_dataclass, is_pydantic_dataclass

# Errors
from pydantic import ValidationError  # from pydantic_core
from pydantic import (
    PydanticUserError, PydanticSchemaGenerationError,
    PydanticInvalidForJsonSchema, PydanticImportError,
    PydanticUndefinedAnnotation, PydanticForbiddenQualifier,
    PydanticErrorCodes,
)

# Experimental
from pydantic.experimental.pipeline import validate_as, transform, validate_as_deferred

# Version
from pydantic import __version__, VERSION
```

---

## Common Patterns

### Model with Full Configuration

```python
from pydantic import BaseModel, ConfigDict, Field, field_validator, computed_field
from typing import Annotated

class User(BaseModel):
    model_config = ConfigDict(
        strict=False,
        frozen=False,
        extra='forbid',
        validate_assignment=True,
        use_attribute_docstrings=True,
        alias_generator=to_camel,
        serialize_by_alias=True,
    )

    name: Annotated[str, Field(min_length=1, max_length=100)]
    age: Annotated[int, Field(ge=0, le=150)]
    email: EmailStr
    tags: list[str] = []

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        return v.strip()

    @computed_field
    @property
    def display_name(self) -> str:
        return f'{self.name} ({self.age})'
```

### Nested Models with Validation

```python
class Address(BaseModel):
    street: str
    city: str
    country: str = 'US'

class User(BaseModel):
    name: str
    addresses: list[Address] = []

    @model_validator(mode='after')
    def check_addresses(self) -> Self:
        if not self.addresses:
            raise ValueError('At least one address required')
        return self
```

### Generic Model

```python
from pydantic import BaseModel
from typing import Generic, TypeVar

T = TypeVar('T')

class Response(BaseModel, Generic[T]):
    data: T
    error: str | None = None

# Usage
IntResponse = Response[int]
response = IntResponse(data=42)
```

### Discriminated Union API Response

```python
from pydantic import BaseModel, Field, RootModel
from typing import Annotated, Literal, Union

class Success(BaseModel):
    status: Literal['ok']
    data: dict

class Error(BaseModel):
    status: Literal['error']
    message: str

class ApiResponse(RootModel):
    root: Annotated[Union[Success, Error], Field(discriminator='status')]
```

### Settings with Environment Variables

```python
# Requires: pip install pydantic-settings
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_prefix='APP_',
        env_file='.env',
    )

    debug: bool = False
    database_url: PostgresDsn
    secret_key: SecretStr
```

---

## Deprecated APIs (V1 -> V2 Migration)

| V1 (Deprecated) | V2 (Use Instead) |
|------------------|-------------------|
| `model.dict()` | `model.model_dump()` |
| `model.json()` | `model.model_dump_json()` |
| `Model.parse_obj(data)` | `Model.model_validate(data)` |
| `Model.parse_raw(json)` | `Model.model_validate_json(json)` |
| `Model.parse_file(path)` | Read file, then `model_validate_json()` |
| `Model.from_orm(obj)` | `Model.model_validate(obj)` with `from_attributes=True` |
| `model.copy()` | `model.model_copy()` |
| `Model.schema()` | `Model.model_json_schema()` |
| `Model.schema_json()` | `json.dumps(Model.model_json_schema())` |
| `Model.validate(data)` | `Model.model_validate(data)` |
| `Model.construct(**data)` | `Model.model_construct(**data)` |
| `Model.update_forward_refs()` | `Model.model_rebuild()` |
| `@validator` | `@field_validator` |
| `@root_validator` | `@model_validator` |
| `class Config:` | `model_config = ConfigDict(...)` |
| `Field(regex=...)` | `Field(pattern=...)` |
| `Field(const=True)` | Use `Literal[value]` type |
| `Field(allow_mutation=False)` | `Field(frozen=True)` |
