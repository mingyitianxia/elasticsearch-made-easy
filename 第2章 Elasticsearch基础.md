## 2.2 Elasticsearch 基础

### 2.2.8 映射

```
PUT kibana_sample_data_flights_001
{
  "mappings": {
    "properties": {
      "AvgTicketPrice": {
        "type": "float"
      },
      "Cancelled": {
        "type": "boolean"
      },
      "Carrier": {
        "type": "keyword"
      }
    }
  }
}
```
