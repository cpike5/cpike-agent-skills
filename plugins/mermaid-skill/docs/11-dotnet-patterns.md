# .NET Architecture Patterns

Ready-to-adapt Mermaid templates for common .NET architectural patterns. Copy the code block, adjust node labels and connections to match your domain.

---

## 1. Clean Architecture

**When to use:** Visualizing layer boundaries and dependency inversion. Dependency arrows point inward; outer layers depend on inner, never the reverse.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1e3a5f", "primaryTextColor": "#ffffff", "primaryBorderColor": "#4a90d9", "lineColor": "#4a90d9", "clusterBkg": "#eef3fb", "clusterBorder": "#aac4e8", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef presentation fill:#1e3a5f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef application  fill:#2d6a9f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef domain       fill:#1a6b3c,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef infra        fill:#7d4e00,stroke:#f39c12,stroke-width:2px,color:#fff

    subgraph Presentation ["Presentation Layer"]
        controllers["Controllers / Blazor Pages"]:::presentation
        viewmodels["ViewModels / DTOs"]:::presentation
    end

    subgraph Application ["Application Layer"]
        usecases["Use Cases / Commands / Queries"]:::application
        interfaces["Port Interfaces\n(IRepository, IEmailService)"]:::application
    end

    subgraph Domain ["Domain Layer (Core)"]
        entities["Entities / Aggregates"]:::domain
        valueobjects["Value Objects"]:::domain
        domainevents["Domain Events"]:::domain
    end

    subgraph Infrastructure ["Infrastructure Layer"]
        repos["EF Core Repositories"]:::infra
        external["External Services\n(SMTP, HTTP, Storage)"]:::infra
        dbctx["DbContext"]:::infra
    end

    controllers --> usecases
    viewmodels --> usecases
    usecases --> entities
    usecases --> interfaces
    repos -.->|implements| interfaces
    external -.->|implements| interfaces
    repos --> dbctx
```

---

## 2. Dependency Injection Container

**When to use:** Explaining service registration and lifetime to team members; onboarding documentation for DI setup in `Program.cs`.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#4f46e5", "primaryTextColor": "#ffffff", "primaryBorderColor": "#6366f1", "lineColor": "#6366f1", "clusterBkg": "#f1f0ff", "clusterBorder": "#c7d2fe", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef entry     fill:#4f46e5,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef container fill:#0d9488,stroke:#14b8a6,stroke-width:2px,color:#fff
    classDef singleton fill:#be185d,stroke:#ec4899,stroke-width:2px,color:#fff
    classDef scoped    fill:#0369a1,stroke:#38bdf8,stroke-width:2px,color:#fff
    classDef transient fill:#6b7280,stroke:#9ca3af,stroke-width:1px,color:#fff
    classDef concrete  fill:#374151,stroke:#6b7280,stroke-width:1px,color:#fff,stroke-dasharray:4 2

    programcs["Program.cs\nWebApplication.CreateBuilder()"]:::entry

    subgraph DI ["ServiceCollection (IServiceCollection)"]
        singletonReg["Singleton\nAddSingleton#lt;T#gt;()"]:::singleton
        scopedReg["Scoped\nAddScoped#lt;T#gt;()"]:::scoped
        transientReg["Transient\nAddTransient#lt;T#gt;()"]:::transient
    end

    singletonImpl["ElasticsearchClient\nIMemoryCache\nILogger"]:::concrete
    scopedImpl["DbContext\nRepository#lt;T#gt;\nCurrentUserService"]:::concrete
    transientImpl["EmailSender\nValidator#lt;T#gt;\nMapper"]:::concrete

    programcs --> DI
    singletonReg --> singletonImpl
    scopedReg --> scopedImpl
    transientReg --> transientImpl

    subgraph Lifetimes ["Lifetime Rules"]
        rule1["Singleton: one instance\nfor app lifetime"]
        rule2["Scoped: one instance\nper HTTP request"]
        rule3["Transient: new instance\nevery resolution"]
    end

    singletonReg -.-> rule1
    scopedReg    -.-> rule2
    transientReg -.-> rule3
```

---

## 3. ASP.NET Core Middleware Pipeline

**When to use:** Explaining request/response pipeline order, middleware insertion points, and short-circuit behavior.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1e3a5f", "primaryTextColor": "#ffffff", "primaryBorderColor": "#4a90d9", "lineColor": "#4a90d9", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart LR
    classDef request  fill:#1a6b3c,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef mw       fill:#1e3a5f,stroke:#4a90d9,stroke-width:1px,color:#fff
    classDef security fill:#7d1e1e,stroke:#e74c3c,stroke-width:2px,color:#fff
    classDef endpoint fill:#4f46e5,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef response fill:#0d9488,stroke:#14b8a6,stroke-width:2px,color:#fff

    req(["HTTP Request"]):::request
    exc["UseExceptionHandler"]:::security
    https["UseHttpsRedirection"]:::mw
    static["UseStaticFiles"]:::mw
    routing["UseRouting"]:::mw
    ratelimit["UseRateLimiter"]:::mw
    auth["UseAuthentication"]:::security
    authz["UseAuthorization"]:::security
    cors["UseCors"]:::mw
    endpoint["MapControllers\nMapBlazorHub\nMapHealthChecks"]:::endpoint
    resp(["HTTP Response"]):::response

    req --> exc --> https --> static --> routing --> ratelimit --> auth --> authz --> cors --> endpoint --> resp

    shortcircuit["Short-circuit:\nReturns response\nwithout continuing pipeline"]
    static -.->|"Static file found"| shortcircuit
    exc    -.->|"Unhandled exception"| shortcircuit
```

---

## 4. CQRS with MediatR

**When to use:** Documenting command/query separation, MediatR dispatch flow, and read/write database split.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1e3a5f", "primaryTextColor": "#ffffff", "primaryBorderColor": "#4a90d9", "lineColor": "#4a90d9", "clusterBkg": "#eef3fb", "clusterBorder": "#aac4e8", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef controller fill:#1e3a5f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef mediator   fill:#4f46e5,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef command    fill:#7d1e1e,stroke:#e74c3c,stroke-width:2px,color:#fff
    classDef query      fill:#0d9488,stroke:#14b8a6,stroke-width:2px,color:#fff
    classDef handler    fill:#1a6b3c,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef db         fill:#374151,stroke:#6b7280,stroke-width:1px,color:#fff

    controller["API Controller\nPOST /orders\nGET /orders/{id}"]:::controller
    mediatr["IMediator\n.Send(request)"]:::mediator

    subgraph WriteStack ["Write Side"]
        cmd["CreateOrderCommand\n{ CustomerId, Items }"]:::command
        cmdhandler["CreateOrderCommandHandler\n: IRequestHandler#lt;CreateOrderCommand, Guid#gt;"]:::handler
        pipeline["Pipeline Behaviors\nValidationBehavior\nLoggingBehavior\nTransactionBehavior"]:::mediator
        writedb[("Write DB\nDbContext\n(EF Core)")]:::db
    end

    subgraph ReadStack ["Read Side"]
        qry["GetOrderQuery\n{ OrderId }"]:::query
        qryhandler["GetOrderQueryHandler\n: IRequestHandler#lt;GetOrderQuery, OrderDto#gt;"]:::handler
        readdb[("Read DB\nReadOnlyDbContext\nor Dapper / Raw SQL")]:::db
    end

    controller --> mediatr
    mediatr --> cmd --> pipeline --> cmdhandler --> writedb
    mediatr --> qry --> qryhandler --> readdb
```

---

## 5. Blazor Component Tree

**When to use:** Documenting Blazor render hierarchy, layout nesting, and render mode annotations.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#4f46e5", "primaryTextColor": "#ffffff", "primaryBorderColor": "#6366f1", "lineColor": "#6366f1", "clusterBkg": "#f1f0ff", "clusterBorder": "#c7d2fe", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef host      fill:#1e3a5f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef layout    fill:#4f46e5,stroke:#6366f1,stroke-width:2px,color:#fff
    classDef page      fill:#0d9488,stroke:#14b8a6,stroke-width:2px,color:#fff
    classDef component fill:#1a6b3c,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef interactive fill:#7d4e00,stroke:#f39c12,stroke-width:2px,color:#fff
    classDef label     fill:none,stroke:none,color:#555

    app["App.razor\n@rendermode: Static SSR"]:::host
    router["Router\nFound / NotFound"]:::host
    mainlayout["MainLayout.razor\n@inherits LayoutComponentBase"]:::layout
    navmenu["NavMenu.razor\n@rendermode: InteractiveServer"]:::interactive
    body["@Body (slot)"]:::layout

    subgraph Pages
        dashboard["Dashboard.razor\n@page #quot;/#quot;\n@rendermode: InteractiveAuto"]:::page
        orders["Orders.razor\n@page #quot;/orders#quot;\n@rendermode: InteractiveServer"]:::page
        profile["Profile.razor\n@page #quot;/profile#quot;\n@rendermode: Static SSR"]:::page
    end

    subgraph Components
        ordergrid["OrderGrid.razor"]:::component
        searchbar["SearchBar.razor"]:::interactive
        chart["SalesChart.razor\n(JS Interop)"]:::interactive
    end

    app --> router --> mainlayout
    mainlayout --> navmenu
    mainlayout --> body
    body --> dashboard
    body --> orders
    body --> profile
    orders --> ordergrid --> searchbar
    dashboard --> chart
```

---

## 6. EF Core Model Relationships

**When to use:** Documenting database schema and entity relationships for a typical blog/content domain.

```mermaid
erDiagram
    BLOG {
        int     Id          PK
        string  Name
        string  Url
        int     OwnerId     FK
    }

    POST {
        int     Id          PK
        string  Title
        string  Content
        bool    IsPublished
        datetime PublishedAt
        int     BlogId      FK
        int     AuthorId    FK
    }

    COMMENT {
        int     Id          PK
        string  Body
        datetime CreatedAt
        int     PostId      FK
        int     AuthorId    FK
    }

    TAG {
        int     Id          PK
        string  Name
        string  Slug
    }

    POST_TAG {
        int     PostId      FK
        int     TagId       FK
    }

    USER {
        int     Id          PK
        string  UserName
        string  Email
    }

    BLOG    ||--o{ POST     : "contains"
    USER    ||--o{ BLOG     : "owns"
    POST    ||--o{ COMMENT  : "has"
    USER    ||--o{ POST     : "authors"
    USER    ||--o{ COMMENT  : "authors"
    POST    ||--o{ POST_TAG : "tagged via"
    TAG     ||--o{ POST_TAG : "applied via"
```

---

## 7. Microservice Topology

**When to use:** C4 Container-level view of a microservice system -- API gateway, downstream services, databases, and async messaging.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#1e3a5f", "primaryTextColor": "#ffffff", "primaryBorderColor": "#4a90d9", "lineColor": "#4a90d9", "clusterBkg": "#eef3fb", "clusterBorder": "#aac4e8", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef gateway  fill:#1e3a5f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef service  fill:#2d6a9f,stroke:#4a90d9,stroke-width:2px,color:#fff
    classDef store    fill:#1a6b3c,stroke:#27ae60,stroke-width:2px,color:#fff
    classDef bus      fill:#7d4e00,stroke:#f39c12,stroke-width:2px,color:#fff
    classDef external fill:#f0f0f0,stroke:#aaaaaa,stroke-width:1px,color:#333,stroke-dasharray:4 2
    classDef client   fill:#4f46e5,stroke:#6366f1,stroke-width:2px,color:#fff

    webclient["Web Client\n(Blazor WASM / SPA)"]:::client
    mobileclient["Mobile Client\n(iOS / Android)"]:::client

    gateway["API Gateway\nYARP / Ocelot\n:443"]:::gateway

    subgraph Services
        ordersvc["Order Service\n:5001"]:::service
        productsvc["Product Service\n:5002"]:::service
        usersvc["User Service\n:5003"]:::service
        notifysvc["Notification Service\n:5004"]:::service
    end

    subgraph Stores
        orderdb[("Orders DB\nAzure SQL")]:::store
        productdb[("Products DB\nAzure SQL")]:::store
        userdb[("Users DB\nPostgreSQL")]:::store
        cache[("Redis Cache")]:::store
    end

    bus["Message Bus\nRabbitMQ + MassTransit"]:::bus

    identityprovider["Identity Provider\nMicrosoft Entra ID"]:::external

    webclient --> gateway
    mobileclient --> gateway
    gateway --> ordersvc
    gateway --> productsvc
    gateway --> usersvc
    gateway -.->|"validates JWT"| identityprovider

    ordersvc --> orderdb
    ordersvc --> cache
    productsvc --> productdb
    productsvc --> cache
    usersvc --> userdb

    ordersvc -->|"OrderPlaced event"| bus
    productsvc -->|"StockReserved event"| bus
    bus --> notifysvc
    bus --> ordersvc
```

---

## 8. Azure Deployment Architecture

**When to use:** Infrastructure and deployment documentation showing Azure PaaS components, connections, and data flows.

```mermaid
%%{init: {"theme": "base", "themeVariables": {"primaryColor": "#0078d4", "primaryTextColor": "#ffffff", "primaryBorderColor": "#005a9e", "lineColor": "#0078d4", "clusterBkg": "#e8f4fd", "clusterBorder": "#90c8f0", "fontFamily": "Segoe UI, sans-serif"}}}%%
flowchart TD
    classDef azure    fill:#0078d4,stroke:#005a9e,stroke-width:2px,color:#fff
    classDef data     fill:#217346,stroke:#185c37,stroke-width:2px,color:#fff
    classDef cache    fill:#dc3545,stroke:#a71d2a,stroke-width:2px,color:#fff
    classDef storage  fill:#6f42c1,stroke:#4e2d87,stroke-width:2px,color:#fff
    classDef monitor  fill:#fd7e14,stroke:#d96a0a,stroke-width:2px,color:#fff
    classDef cdn      fill:#20c997,stroke:#198754,stroke-width:2px,color:#fff
    classDef user     fill:#495057,stroke:#343a40,stroke-width:1px,color:#fff

    users["End Users\n(Browser / Mobile)"]:::user

    subgraph EdgeLayer ["Edge"]
        cdn["Azure CDN / Front Door\nGlobal Load Balancing\nWAF Rules"]:::cdn
    end

    subgraph ComputeLayer ["Compute (australiaeast)"]
        appservice["App Service Plan (P2v3)\nASP.NET Core + Blazor\nAuto-scale: 1–5 instances"]:::azure
        appservice2["Staging Slot\n(deployment swap target)"]:::azure
    end

    subgraph DataLayer ["Data"]
        sqlserver[("Azure SQL\nGeneral Purpose, 4 vCores\nGeo-redundant backup")]:::data
        redis[("Azure Cache for Redis\nC2 Standard\nSession + Output Cache")]:::cache
        blob["Azure Blob Storage\nLRS -- user uploads\nlife cycle policy: 90d"]:::storage
    end

    subgraph ObservabilityLayer ["Observability"]
        appinsights["Application Insights\nLive Metrics\nDistributed Tracing"]:::monitor
        loganalytics["Log Analytics Workspace\nRetention: 90 days"]:::monitor
    end

    keyvault["Azure Key Vault\nSecrets + Certs\nManaged Identity access"]:::azure

    users --> cdn --> appservice
    appservice --> sqlserver
    appservice --> redis
    appservice --> blob
    appservice --> appinsights
    appinsights --> loganalytics
    appservice -.->|"Managed Identity"| keyvault
    appservice -.->|"slot swap"| appservice2
```
