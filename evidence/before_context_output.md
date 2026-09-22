# Before Context Engineering — Raw LLM Outputs

These outputs were generated using a **generic system prompt** with no CLAUDE.md:

```
System: "You are a helpful API documentation assistant. Answer questions about the API."
```

The same 3 questions were re-run with CLAUDE.md loaded — see after_context_output.md for comparison.

---

## Query 1: "Which endpoint do I call to get a customer's order history?"

**Retrieved chunks:** Same 5 chunks as after (retrieval is identical — only the system prompt differs)

**LLM Response (no CLAUDE.md):**

> You can retrieve a customer's order history by calling the orders endpoint and filtering
> by the customer's ID. Make a GET request to the orders service and pass the customerId as
> a query parameter to get all orders associated with that customer. You may also want to
> add date range filters if you only need recent orders.

**Issues:**
- No HTTP method stated
- No endpoint path given (`/api/v1/orders` not mentioned)
- No authentication requirement mentioned
- No parameter types or names given precisely
- No source citation

---

## Query 2: "How do I refresh an expired JWT token?"

**LLM Response (no CLAUDE.md):**

> When your JWT access token expires, you'll need to use a refresh token to get a new one.
> Most APIs have a refresh endpoint where you can POST your refresh token to receive a new
> access token. Check your authentication service documentation for the specific endpoint path
> and request format.

**Issues:**
- Literally tells the developer to "check your documentation" — useless
- No path (`/api/v1/auth/refresh`) given
- No request body format shown
- No mention of what happens when the refresh token itself expires
- No source citation

---

## Query 3: "How do I check if a product is in stock?"

**LLM Response (no CLAUDE.md):**

> To check product inventory, you would typically call an inventory or product endpoint.
> You can pass the product ID and the service will return the current stock level.
> Make sure you have the correct authentication headers set up before making the request.

**Issues:**
- "inventory or product endpoint" — vague, doesn't choose
- No path, no HTTP method
- "Make sure you have correct authentication headers" — tells developer nothing actionable
- No distinction between `totalStock` vs `availableStock` (a critical distinction)
- No source citation

---

## Summary of before-state problems

| Problem | Frequency |
|---------|-----------|
| Missing HTTP method | 3/3 queries |
| Missing endpoint path | 3/3 queries |
| Missing source citation | 3/3 queries |
| Missing auth header format | 3/3 queries |
| Vague or generic language | 3/3 queries |
| Missing parameter names/types | 3/3 queries |
