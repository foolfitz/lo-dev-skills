# C++ Implementation Patterns

## Pattern 1: Simple Service

The most common pattern for implementing a UNO service. Uses `cppu::WeakImplHelper` to provide reference counting and interface querying.

**Based on:** `toolkit/source/awt/asynccallback.cxx`

```cpp
#include <sal/config.h>
#include <cppuhelper/implbase.hxx>
#include <cppuhelper/supportsservice.hxx>
#include <com/sun/star/lang/XServiceInfo.hpp>
#include <com/sun/star/uno/XComponentContext.hpp>
#include <com/sun/star/awt/XMyInterface.hpp>

namespace {

class MyService :
    public cppu::WeakImplHelper<
        css::lang::XServiceInfo,
        css::awt::XMyInterface>
{
public:
    MyService() = default;
    MyService(const MyService&) = delete;
    MyService& operator=(const MyService&) = delete;

    // XServiceInfo
    OUString SAL_CALL getImplementationName() override
    {
        return u"com.sun.star.awt.comp.MyService"_ustr;
    }

    sal_Bool SAL_CALL supportsService(const OUString& ServiceName) override
    {
        return cppu::supportsService(this, ServiceName);
    }

    css::uno::Sequence<OUString> SAL_CALL getSupportedServiceNames() override
    {
        return { u"com.sun.star.awt.MyService"_ustr };
    }

    // XMyInterface methods
    void SAL_CALL myMethod(const OUString& arg) override
    {
        // Implementation here
    }

private:
    virtual ~MyService() override = default;
};

} // anonymous namespace

// Constructor function — name must match .component XML
extern "C" SAL_DLLPUBLIC_EXPORT css::uno::XInterface*
com_sun_star_awt_comp_MyService_get_implementation(
    css::uno::XComponentContext*,
    css::uno::Sequence<css::uno::Any> const&)
{
    return cppu::acquire(new MyService());
}
```

**Key elements:**
- Anonymous namespace for the implementation class
- `cppu::WeakImplHelper` handles `XInterface`, reference counting, and `queryInterface()`
- XServiceInfo is mandatory for all services
- Use `cppu::supportsService()` helper — never implement manually
- Constructor function is `extern "C"` with `SAL_DLLPUBLIC_EXPORT`
- Destructor is `private` and `virtual` — prevents stack allocation

## Pattern 2: Service with XComponentContext

When the service needs access to the component context (for creating other services):

```cpp
class MyService :
    public cppu::WeakImplHelper<css::lang::XServiceInfo, css::awt::XMyInterface>
{
public:
    explicit MyService(css::uno::Reference<css::uno::XComponentContext> xContext)
        : m_xContext(std::move(xContext))
    {}

    // ... XServiceInfo methods same as above ...

    void SAL_CALL myMethod() override
    {
        // Use m_xContext to create other services
        auto xSMgr = m_xContext->getServiceManager();
        auto xService = xSMgr->createInstanceWithContext(
            u"com.sun.star.awt.Toolkit"_ustr, m_xContext);
    }

private:
    css::uno::Reference<css::uno::XComponentContext> m_xContext;
};

extern "C" SAL_DLLPUBLIC_EXPORT css::uno::XInterface*
com_sun_star_awt_comp_MyService_get_implementation(
    css::uno::XComponentContext* pContext,
    css::uno::Sequence<css::uno::Any> const&)
{
    return cppu::acquire(new MyService(pContext));
}
```

## Pattern 3: VCL-Backed Implementation

For services that wrap VCL (Visual Components Library) widgets. Requires `SolarMutexGuard` for thread safety.

**Based on:** `toolkit/source/awt/vclxgraphics.cxx`

```cpp
#include <vcl/svapp.hxx>
#include <vcl/outdev.hxx>
#include <toolkit/awt/vclxdevice.hxx>

class VCLXMyWidget : public cppu::ImplInheritanceHelper<VCLXWindow, css::awt::XMyWidget>
{
public:
    VCLXMyWidget() = default;

    // XMyWidget
    void SAL_CALL doSomething() override
    {
        SolarMutexGuard aGuard;  // REQUIRED for VCL access
        VclPtr<vcl::Window> pWindow = GetWindow();
        if (!pWindow)
            return;
        // Use pWindow...
    }
};
```

**SolarMutexGuard rules:**
- **Always acquire** before accessing any VCL object (Window, OutputDevice, etc.)
- **Do not hold** while calling back into UNO (risk of deadlock)
- Prefer `SolarMutexGuard` over `SolarMutexReleaser`
- VCL objects use `VclPtr<T>` smart pointers, not raw pointers

## Pattern 4: Listener Multiplexer

For dispatching events to multiple registered listeners. Uses macros from `toolkit/helper/macros.hxx`.

**Based on:** `include/toolkit/helper/listenermultiplexer.hxx`

**Declaration (in header):**
```cpp
#include <toolkit/helper/macros.hxx>
#include <toolkit/helper/listenermultiplexer.hxx>

DECL_LISTENERMULTIPLEXER_START(PaintListenerMultiplexer, css::awt::XPaintListener)
    void SAL_CALL windowPaint(const css::awt::PaintEvent& e) override;
DECL_LISTENERMULTIPLEXER_END
```

**Implementation (in .cxx):**
```cpp
IMPL_LISTENERMULTIPLEXER_BASEMETHODS(PaintListenerMultiplexer, css::awt::XPaintListener)
IMPL_LISTENERMULTIPLEXER_LISTENERMETHOD(PaintListenerMultiplexer, css::awt::XPaintListener, windowPaint, css::awt::PaintEvent)
```

**Using the multiplexer in a component:**
```cpp
class MyComponent : public cppu::WeakImplHelper<css::awt::XWindow>
{
public:
    MyComponent() : maPaintListeners(*this) {}

    void SAL_CALL addPaintListener(
        const css::uno::Reference<css::awt::XPaintListener>& l) override
    {
        maPaintListeners.addInterface(l);
    }

    void SAL_CALL removePaintListener(
        const css::uno::Reference<css::awt::XPaintListener>& l) override
    {
        maPaintListeners.removeInterface(l);
    }

private:
    PaintListenerMultiplexer maPaintListeners;
};
```

## Pattern 5: Dispose Pattern

For components that hold resources and need explicit cleanup:

```cpp
class MyComponent :
    public cppu::WeakComponentImplHelper<css::lang::XServiceInfo, css::awt::XMyInterface>
{
public:
    MyComponent()
        : cppu::WeakComponentImplHelper<css::lang::XServiceInfo, css::awt::XMyInterface>(m_aMutex)
    {}

protected:
    // Called when last reference is released or dispose() is called
    void SAL_CALL disposing() override
    {
        // Release all resources
        m_xOtherService.clear();
    }

private:
    std::mutex m_aMutex;
    css::uno::Reference<css::uno::XInterface> m_xOtherService;
};
```

**Note:** Use `WeakComponentImplHelper` instead of `WeakImplHelper` when you need dispose support.

## Common Includes Reference

| You need... | Include |
|-------------|---------|
| `WeakImplHelper` | `<cppuhelper/implbase.hxx>` |
| `WeakComponentImplHelper` | `<cppuhelper/compbase.hxx>` |
| `ImplInheritanceHelper` | `<cppuhelper/implbase.hxx>` |
| `supportsService()` | `<cppuhelper/supportsservice.hxx>` |
| `XServiceInfo` | `<com/sun/star/lang/XServiceInfo.hpp>` |
| `XComponentContext` | `<com/sun/star/uno/XComponentContext.hpp>` |
| `SolarMutexGuard` | `<vcl/svapp.hxx>` |
| `OUString` | `<rtl/ustring.hxx>` (usually auto-included) |
| Generated UNO header | `<com/sun/star/<module>/<Type>.hpp>` |
| Listener macros | `<toolkit/helper/macros.hxx>` |
| ListenerMultiplexerBase | `<toolkit/helper/listenermultiplexer.hxx>` |

## UNO String Literals

Modern LO code uses `_ustr` suffix for UNO string literals:

```cpp
// Correct (modern)
return u"com.sun.star.awt.MyService"_ustr;

// Also in sequences
return { u"com.sun.star.awt.MyService"_ustr };
```

## Exception Handling

```cpp
// Throwing UNO exceptions
throw css::lang::IllegalArgumentException(
    u"Invalid parameter"_ustr,
    static_cast<cppu::OWeakObject*>(this),
    0 /* argument index */);

// Catching and converting
try {
    // ...
} catch (const css::uno::Exception& e) {
    SAL_WARN("module", "Error: " << e.Message);
}
```

## Thread Safety Summary

| Scenario | Solution |
|----------|----------|
| Accessing VCL objects | `SolarMutexGuard aGuard;` |
| Protecting member variables | `std::unique_lock g(m_aMutex);` |
| Calling back into UNO from VCL | Release SolarMutex first: `SolarMutexReleaser aReleaser;` |
| Async operations | Use `Application::PostUserEvent()` (see asynccallback.cxx) |
| Listener iteration | Use `OInterfaceIteratorHelper4` with mutex |
