# Common Base Interfaces Quick Reference

## Core Interfaces

### XInterface
**Module:** `com::sun::star::uno`
**Purpose:** Root interface for all UNO objects. Provides reference counting and interface querying.

| Method | Description |
|--------|-------------|
| `queryInterface(Type)` | Returns the requested interface or empty Any |
| `acquire()` | Increment reference count |
| `release()` | Decrement reference count |

**Note:** Implemented automatically by `cppu::WeakImplHelper`. Never implement manually.

### XServiceInfo
**Module:** `com::sun::star::lang`
**Purpose:** Identifies the service implementation. Required for all services.

| Method | Description |
|--------|-------------|
| `getImplementationName()` | Returns unique implementation name |
| `supportsService(name)` | Checks if a service name is supported |
| `getSupportedServiceNames()` | Returns all supported service names |

**Implementation tip:** Use `cppu::supportsService(this, serviceName)` for `supportsService()`.

### XComponent
**Module:** `com::sun::star::lang`
**Purpose:** Lifecycle management with explicit dispose.

| Method | Description |
|--------|-------------|
| `dispose()` | Release resources and notify listeners |
| `addEventListener(XEventListener)` | Register for dispose notification |
| `removeEventListener(XEventListener)` | Unregister |

**Implementation tip:** Use `cppu::WeakComponentImplHelper` instead of `WeakImplHelper`.

### XEventListener
**Module:** `com::sun::star::lang`
**Purpose:** Base interface for all event listeners.

| Method | Description |
|--------|-------------|
| `disposing(EventObject)` | Called when the source is being disposed |

**Note:** All listener interfaces inherit from this. The `disposing()` method is for cleanup.

## Initialization & Configuration

### XInitialization
**Module:** `com::sun::star::lang`
**Purpose:** Initialize a service with parameters after construction.

| Method | Description |
|--------|-------------|
| `initialize(sequence<any>)` | Called with initialization arguments |

**Use when:** The service needs configuration that can't be passed via the constructor function.

### XPropertySet
**Module:** `com::sun::star::beans`
**Purpose:** Get/set named properties on an object.

| Method | Description |
|--------|-------------|
| `getPropertyValue(name)` | Get property value as Any |
| `setPropertyValue(name, value)` | Set property value |
| `addPropertyChangeListener(...)` | Listen for property changes |
| `removePropertyChangeListener(...)` | Stop listening |
| `getPropertySetInfo()` | Get metadata about available properties |

**Implementation tip:** Use `cppu::PropertySetMixin` or `comphelper::PropertySetMixin` for boilerplate.

### XMultiPropertySet
**Module:** `com::sun::star::beans`
**Purpose:** Batch get/set of multiple properties (more efficient).

## UI & Window Interfaces

### XWindow
**Module:** `com::sun::star::awt`
**Purpose:** Basic window operations.

| Method | Description |
|--------|-------------|
| `setPosSize(x, y, w, h, flags)` | Set window position and size |
| `setVisible(bool)` | Show/hide window |
| `setEnable(bool)` | Enable/disable window |
| `addWindowListener(l)` | Listen for resize/move |
| `addKeyListener(l)` | Listen for keyboard events |
| `addMouseListener(l)` | Listen for mouse events |

### XControl
**Module:** `com::sun::star::awt`
**Purpose:** UNO control lifecycle (model-view separation).

| Method | Description |
|--------|-------------|
| `setModel(XControlModel)` | Set the data model |
| `getModel()` | Get the data model |
| `createPeer(toolkit, parent)` | Create the native widget |
| `getPeer()` | Get the native widget peer |

## Document Interfaces

### XTextDocument
**Module:** `com::sun::star::text`
**Purpose:** Access to Writer document content.

### XSpreadsheetDocument
**Module:** `com::sun::star::sheet`
**Purpose:** Access to Calc document content.

### XDrawPagesSupplier
**Module:** `com::sun::star::drawing`
**Purpose:** Access to Draw/Impress pages.

## Commonly Used Together

| Task | Interfaces to implement |
|------|------------------------|
| Basic service | `XServiceInfo` |
| Service with lifecycle | `XServiceInfo` + `XComponent` |
| Service with config | `XServiceInfo` + `XInitialization` |
| Service with properties | `XServiceInfo` + `XPropertySet` |
| Event listener | Specific `XFooListener` (inherits `XEventListener`) |
| UI control | `XServiceInfo` + `XControl` + `XWindow` |
