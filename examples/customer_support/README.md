# Customer Support RAG Evaluation Example

This folder contains a complete customer support evaluation suite demonstrating how to write test cases for a production chatbot.

## File Contents

- `customer_support.yml`: The test suite file defining the target (mock) and 3 test cases.
  - `refund-policy-days`: Thai-language query validating refund periods and source citations.
  - `pii-safety-block`: Safety test verifying refusal heuristic triggers.
  - `shipping-duration`: English-language query validating shipping options and RAG matching.

## Running this Example

You can execute the evaluation suite by running:

```bash
agentaudit run examples/customer_support/customer_support.yml
```

To see verbose assertion checking lines:

```bash
agentaudit run examples/customer_support/customer_support.yml --verbose
```
