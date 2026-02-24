# .NET Elasticsearch Client

## Official Client: Elastic.Clients.Elasticsearch

- **NuGet**: `Elastic.Clients.Elasticsearch`
- Targets Elasticsearch **8.x only**
- Uses **System.Text.Json** (not Newtonsoft.Json)
- Fully async API (all operations return `Task`)

### Client Creation

**Single node:**

```csharp
var settings = new ElasticsearchClientSettings(new Uri("https://localhost:9200"))
    .Authentication(new ApiKey("base64-api-key"))
    .CertificateFingerprint("hex-sha256-fingerprint");

var client = new ElasticsearchClient(settings);
```

**Multi-node:**

```csharp
var pool = new StaticNodePool(new[]
{
    new Uri("https://node1:9200"),
    new Uri("https://node2:9200"),
    new Uri("https://node3:9200")
});

var settings = new ElasticsearchClientSettings(pool)
    .Authentication(new BasicAuthentication("elastic", "changeme"));

var client = new ElasticsearchClient(settings);
```

**Elastic Cloud:**

```csharp
var settings = new ElasticsearchClientSettings("deployment-name:region:cloud-id-hash", new ApiKey("base64-api-key"));

var client = new ElasticsearchClient(settings);
```

### ElasticsearchClientSettings Configuration

| Setting | Description | Example |
|---------|-------------|---------|
| `Authentication(ApiKey)` | API key auth (**recommended**) | `.Authentication(new ApiKey("key"))` |
| `Authentication(BasicAuthentication)` | Username/password auth | `.Authentication(new BasicAuthentication("user", "pass"))` |
| `CertificateFingerprint` | TLS cert fingerprint for self-signed certs | `.CertificateFingerprint("AB:CD:EF:...")` |
| `RequestTimeout` | Per-request timeout | `.RequestTimeout(TimeSpan.FromSeconds(30))` |
| `MaxRetries` | Retry count on failure | `.MaxRetries(3)` |
| `EnableDebugMode` | Captures request/response bytes for debugging | `.EnableDebugMode()` |
| `DefaultMappingFor<T>` | Set index name and ID property per type | See below |

**DefaultMappingFor<T>:**

```csharp
var settings = new ElasticsearchClientSettings(new Uri("https://localhost:9200"))
    .DefaultMappingFor<Product>(m => m
        .IndexName("products")
        .IdProperty(p => p.ProductId)
    )
    .DefaultMappingFor<Order>(m => m
        .IndexName("orders")
        .IdProperty(o => o.OrderId)
    );
```

### Document Operations

**Index a document:**

```csharp
var product = new Product { ProductId = "1", Name = "Widget", Price = 9.99m };

var response = await client.IndexAsync(product, idx => idx
    .Index("products")
    .Id(product.ProductId)
);
```

**Get a document:**

```csharp
var response = await client.GetAsync<Product>("1", g => g.Index("products"));

if (response.Found)
{
    Product product = response.Source;
}
```

**Update a document (partial doc):**

```csharp
var response = await client.UpdateAsync<Product, object>("products", "1", u => u
    .Doc(new { Price = 12.99m })
);
```

**Update a document (script):**

```csharp
var response = await client.UpdateAsync<Product, Product>("products", "1", u => u
    .Script(s => s
        .Source("ctx._source.price += params.increase")
        .Params(p => p.Add("increase", 5))
    )
);
```

**Delete a document:**

```csharp
var response = await client.DeleteAsync("products", "1");
```

### Search

**Fluent API search:**

```csharp
var response = await client.SearchAsync<Product>(s => s
    .Index("products")
    .From(0)
    .Size(20)
    .Query(q => q
        .Bool(b => b
            .Must(
                m => m.Match(mt => mt.Field(f => f.Name).Query("widget")),
                m => m.Range(r => r.NumberRange(nr => nr.Field(f => f.Price).Gte(5).Lte(50)))
            )
            .Filter(
                f => f.Term(t => t.Field(ff => ff.Category).Value("electronics"))
            )
        )
    )
    .Sort(so => so
        .Field(f => f.Price, new FieldSort { Order = SortOrder.Asc })
    )
);

foreach (var hit in response.Documents)
{
    Console.WriteLine($"{hit.Name}: {hit.Price}");
}
```

### Aggregations

```csharp
var response = await client.SearchAsync<Product>(s => s
    .Index("products")
    .Size(0)
    .Aggregations(aggs => aggs
        .Add("avg_price", a => a.Avg(avg => avg.Field(f => f.Price)))
        .Add("categories", a => a.Terms(t => t
            .Field(f => f.Category)
            .Size(10)
        ))
    )
);

var avgPrice = response.Aggregations!.GetAverage("avg_price")!.Value;
var categories = response.Aggregations!.GetStringTerms("categories")!.Buckets;

foreach (var bucket in categories)
{
    Console.WriteLine($"{bucket.Key}: {bucket.DocCount}");
}
```

### Index Creation

```csharp
var response = await client.Indices.CreateAsync("products", c => c
    .Settings(s => s
        .NumberOfShards(1)
        .NumberOfReplicas(1)
    )
    .Mappings(m => m
        .Properties<Product>(p => p
            .Keyword(k => k.ProductId)
            .Text(t => t.Name, t => t.Analyzer("standard"))
            .Keyword(k => k.Category)
            .FloatNumber(f => f.Price)
            .Date(d => d.CreatedAt)
        )
    )
);
```

### Mapping Attributes

- Uses **System.Text.Json** attributes -- **not** NEST attributes
- `[JsonPropertyName]` controls serialized field name
- `[JsonIgnore]` excludes properties from serialization

```csharp
public class Product
{
    [JsonPropertyName("product_id")]
    public string ProductId { get; set; } = default!;

    [JsonPropertyName("name")]
    public string Name { get; set; } = default!;

    [JsonPropertyName("price")]
    public decimal Price { get; set; }

    [JsonPropertyName("category")]
    public string Category { get; set; } = default!;

    [JsonPropertyName("created_at")]
    public DateTimeOffset CreatedAt { get; set; }

    [JsonIgnore]
    public string InternalNote { get; set; } = default!;
}
```

### Bulk Operations

**BulkAsync with IndexMany:**

```csharp
var products = GetProducts(); // IEnumerable<Product>

var response = await client.BulkAsync(b => b
    .Index("products")
    .IndexMany(products)
);

if (response.Errors)
{
    foreach (var item in response.ItemsWithErrors)
    {
        Console.WriteLine($"Failed: {item.Id} - {item.Error?.Reason}");
    }
}
```

**BulkAll observable for large datasets:**

```csharp
var bulkAll = client.BulkAll(products, b => b
    .Index("products")
    .BackOffRetries(3)
    .BackOffTime(TimeSpan.FromSeconds(5))
    .MaxDegreeOfParallelism(4)
    .Size(1000)
);

var observer = bulkAll.Wait(TimeSpan.FromMinutes(10), response =>
{
    Console.WriteLine($"Indexed page {response.Page}");
});
```

- `Size` -- documents per bulk request
- `MaxDegreeOfParallelism` -- concurrent bulk requests
- `BackOffRetries` / `BackOffTime` -- retry on `429 Too Many Requests`

## NEST vs Elastic.Clients.Elasticsearch

| Dimension | NEST (7.x) | Elastic.Clients.Elasticsearch (8.x) |
|-----------|-----------|--------------------------------------|
| **Target ES version** | 7.x | 8.x |
| **NuGet package** | `NEST` | `Elastic.Clients.Elasticsearch` |
| **Serializer** | Newtonsoft.Json (built-in) | System.Text.Json |
| **Mapping attributes** | `[Text]`, `[Keyword]`, `[Nested]` | `[JsonPropertyName]`, `[JsonIgnore]` |
| **Connection class** | `ConnectionSettings` | `ElasticsearchClientSettings` |
| **Client class** | `ElasticClient` | `ElasticsearchClient` |
| **Connection pool** | `ConnectionPool` | `NodePool` |
| **Query DSL** | `QueryContainer` / operator overloads | Fluent lambda API |
| **Aggregation access** | `.Aggregations.Terms("name")` | `.Aggregations!.GetStringTerms("name")` |
| **LINQ support** | Yes (via `ElasticLinqQueryable`) | No |
| **Auto-mapping** | `.AutoMap()` | Explicit property mapping |
| **Inferred index names** | `[ElasticsearchType]` | `DefaultMappingFor<T>` |
| **Bulk helpers** | `BulkAll` observable | `BulkAll` observable (similar API) |
| **Security model** | Basic auth, API key, cert | API key (**preferred**), basic auth, cert fingerprint |
| **Maintenance status** | Legacy -- no new features | Active development |

## NEST Migration Notes

- **Side-by-side coexistence** is possible -- both packages can be installed simultaneously during migration
- New client **lacks some NEST features**: no LINQ queries, no operator-overloaded bool queries, no auto-mapping
- **Attribute migration**: replace all `[Text]`, `[Keyword]`, `[Nested]` with `[JsonPropertyName("field_name")]`
- **Connection migration**: `ConnectionSettings` becomes `ElasticsearchClientSettings`, `ElasticClient` becomes `ElasticsearchClient`
- **Serializer migration**: remove all Newtonsoft.Json `[JsonProperty]` attributes, replace with `[JsonPropertyName]`
- **Query migration**: rewrite `QueryContainer` / operator overload queries to fluent lambda API

## Low-Level Client: Elasticsearch.Net

- **When to use**: unsupported endpoints, raw JSON requests, maximum control
- Package: `Elastic.Transport` (ships with high-level client)

```csharp
var response = await client.Transport
    .RequestAsync<StringResponse>(HttpMethod.GET, "/_cat/indices", PostData.Empty);

if (response.ApiCallDetails.HttpStatusCode == 200)
{
    Console.WriteLine(response.Body);
}
```

**Raw JSON query:**

```csharp
var json = """
{
  "query": {
    "match": {
      "name": "widget"
    }
  }
}
""";

var response = await client.Transport
    .RequestAsync<StringResponse>(HttpMethod.POST, "/products/_search", PostData.String(json));
```

## Common Mistakes

- **Using NEST for Elasticsearch 8.x** -- NEST targets 7.x only; use `Elastic.Clients.Elasticsearch` for 8.x
- **Using `[JsonProperty]` (Newtonsoft.Json)** -- the new client uses System.Text.Json; use `[JsonPropertyName]` instead
- **Forgetting `await` on async operations** -- all client methods are async; missing `await` silently ignores errors and results
- **Not setting `DefaultMappingFor<T>`** -- without it, the client infers index names from the type name (lowercased), which rarely matches your actual index names
- **Using `EnableDebugMode` in production** -- captures full request/response bodies in memory; use only for development and troubleshooting
- **Not checking `response.IsValidResponse`** -- Elasticsearch returns 200 for partial failures (e.g., bulk with errors); always check the response
