# Python Engineer Skill - Extended

## Core Competencies
- Python best practices and modern patterns
- Async/await programming with asyncio
- Type hints and static analysis
- Code quality and linting
- Testing strategies
- Dependency management

## Known Issues in Wallpicker App

### Critical Async/Await Misuse
**Problem**: WallpaperSetter.set_wallpaper() is async but called synchronously in UI layers, causing silent failures where wallpapers appear set but operations never execute.

**Affected Areas**:
- UI views calling set_wallpaper without await
- Test methods expecting bool but getting coroutine objects
- Mixed sync/async service patterns

**Solution**: Make WallpaperSetter synchronous for UI operations, or properly await in async contexts.

### Type Safety Violations
**Problem**: Missing type annotations throughout UI and service layers, leading to runtime errors and poor IDE support.

**Examples**:
- UI component methods lacking return types
- Service constructors missing parameter hints
- Inconsistent typing in domain models

**Solution**: Add comprehensive PEP 484/585 type hints, especially for GTK callback functions.

### Testing Failures Due to Async
**Problem**: Tests calling async methods without await, expecting sync results.

**Pattern**: 
```python
# Wrong
result = setter.set_wallpaper(path)  # Returns coroutine
assert result is True  # Fails

# Right  
result = await setter.set_wallpaper(path)
assert result is True
```

### Code Quality Issues
- Import organization (ruff I001 errors)
- Unused imports (F401)
- Wrong import sources (collections.abc vs typing)
- Module level imports not at top (E402)

**Solution**: Run `ruff check --fix` and `ruff format` for auto-fixes.

### Error Handling Patterns
- Inconsistent logging (mix of BaseService and direct logging)
- Bare except clauses without logging
- Generic Exception catching hiding specific issues

**Solution**: Standardize on BaseService logging pattern, use specific exception types.

### Dependency Injection Issues
**Problem**: DI container returns `object` instead of generic type `T`, causing type checker errors.

**Affected**: `src/core/container.py:46` - get() method type annotation incorrect.

**Solution**: Fix generic type handling in ServiceContainer.

### ViewModel Property Misuse
**Problem**: GObject.Property setters accessed incorrectly, causing "setter" attribute errors.

**Affected**: `src/ui/view_models/favorites_view_model.py` - properties defined as methods instead of GObject.Property.

**Solution**: Use proper GObject.Property syntax for observable properties.

### Service Injection Type Safety
**Problem**: Services injected as optional (None) but ViewModels expect non-optional types.

**Affected**: `src/ui/main_window.py` - multiple injection points where None is passed to required parameters.

**Solution**: Make DI container guarantee non-None services or add proper null checks.

## Best Practices for Python GTK Apps
- Use asyncio with GLibEventLoopPolicy for GTK integration
- Avoid blocking operations in UI callbacks
- Proper memory management with weak references
- Comprehensive type hints for maintainability