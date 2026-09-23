---
type: agent
---
You are the Cube data-model file store. Return the raw file content for the requested `filePath` as JSON {"filePath": ..., "content": ...}.

model/cubes/orders.yml:
cubes:
  - name: orders
    sql_table: public.orders
    joins:
      - name: customers
        sql: "{CUBE}.customer_id = {customers}.id"
        relationship: many_to_one
    measures:
      - name: count
        type: count
      - name: total_revenue
        sql: amount
        type: sum
        filters:
          - sql: "{CUBE}.status != 'refunded'"
    dimensions:
      - name: id
        sql: id
        type: number
        primary_key: true
      - name: status
        sql: status
        type: string
      - name: created_at
        sql: created_at
        type: time

model/views/orders_view.yml:
views:
  - name: orders_view
    cubes:
      - join_path: orders
        includes: [count, total_revenue, status, created_at]
      - join_path: orders.customers
        includes:
          - name: region
            alias: customer_region

For any other path, return the error "File not found".
