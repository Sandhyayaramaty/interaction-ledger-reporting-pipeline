# AI Usage Disclosure

## 1. AI Tool Used

ChatGPT was used as an AI-assisted development tool during the implementation of Assignment A: Interaction Ledger & Reporting Pipeline.

## 2. How I Used AI

I primarily used AI as a technical assistant to explore possible solutions and discuss implementation approaches.

My approach was to:

- Provide the assignment requirements and explain the expected functionality.
- Ask AI to suggest suitable approaches for different components of the system.
- Discuss alternative solutions, understand their trade-offs, and select the approaches that best suited the requirements.
- Use the selected approaches as a starting point for implementation.
- Request help with Python, PostgreSQL, SQL queries, debugging, and test-case design whenever needed.
- Review the suggestions and make modifications to better fit the project structure, requirements, and actual execution results.

## 3. My Involvement

I drove the implementation by defining what needed to be built, evaluating the suggested approaches, and deciding how the different components should work together.

I configured the development environment and PostgreSQL database, integrated the implementation into the project, executed the pipeline, inspected the generated reports, and made further modifications based on the results.

I did not simply accept every suggestion as-is. I reviewed the proposed solutions, made changes where necessary, and verified the behavior through local execution and testing.

## 4. Examples of AI-Assisted Development

- **Architecture and database design:** Shared the assignment requirements and explored suitable database structures and processing workflows before selecting an implementation approach.
- **Data ingestion and validation:** Discussed approaches for handling inconsistent CSV headers, phone normalization, optional fields, duplicate leads, and validation errors.
- **Event processing:** Explored event deduplication, timestamp handling, orphan-event retention, event-to-lead linking, and disposition processing.
- **PII protection:** Evaluated approaches for encrypting sensitive information while supporting deterministic identity matching.
- **Reporting:** Discussed how to calculate lead buckets, call metrics, daily summaries, and data-quality statistics.
- **Debugging and refinement:** Used AI suggestions to investigate issues, then modified the implementation based on actual database results, generated reports, and test outcomes.

## 5. Testing and Verification

I executed the implementation locally and validated it against both the supplied dataset and a separately generated dataset with a different seed.

I also reran the pipeline to verify that repeated execution did not create duplicate records.

The complete automated test suite was executed locally:

```text
Ran 52 tests
OK
```

## 6. Responsibility

AI served as a source of implementation guidance and alternative approaches. I evaluated the suggestions, selected suitable solutions, made modifications, integrated the components, and verified the final implementation.

I take responsibility for the submitted code and the engineering decisions made throughout the project.