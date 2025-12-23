-- Insert sample documents
INSERT INTO documents (original_filename, filename, file_type, content, file_size, processed, indexed, chunk_count)
VALUES (
    'sample1.txt',
    '/data/raw/sample1.txt',
    'txt',
    'Mortgage Eligibility Requirements

To qualify for a mortgage refinancing, borrowers must meet the following criteria:

1. Credit Score: Applicants must have a minimum credit score of 620. A higher credit score (above 740) typically results in better interest rates and terms.

2. Debt-to-Income Ratio: The total monthly debt payments (including the new mortgage) must not exceed 43% of gross monthly income. Some lenders may allow up to 50% for well-qualified borrowers.

3. Home Equity: Borrowers must have at least 15-20% equity in their home. This is calculated as the difference between the home''s current market value and the outstanding mortgage balance.

4. Income Verification: Applicants must provide recent pay stubs, W-2 forms, and tax returns to verify income stability. Self-employed individuals may need additional documentation.

5. Employment History: A consistent employment history of at least 2 years is required. Recent job changes may require explanation.

6. Property Appraisal: An appraisal is required to determine the current value of the property, which affects loan approval and terms.

Processing typically takes 30-45 days from application to closing.',
    8500,
    TRUE,
    TRUE,
    18
);

INSERT INTO documents (original_filename, filename, file_type, content, file_size, processed, indexed, chunk_count)
VALUES (
    'sample2.txt',
    '/data/raw/sample2.txt',
    'txt',
    'Interest Rates and Terms

Current mortgage rates (as of 2025):

- 30-year fixed: 6.8% - 7.2%
- 15-year fixed: 6.2% - 6.6%
- 5/1 ARM: 5.5% - 5.9%
- 7/1 ARM: 5.8% - 6.2%

Rates vary based on:
1. Credit score (620-750+ gets better rates)
2. Debt-to-income ratio
3. Loan-to-value ratio
4. Down payment size
5. Current market conditions

Refinancing savings typically require 1-3 years to break even on closing costs.

Additional fees may include:
- Origination fee: 0.5% - 1% of loan amount
- Processing fee: $300 - $500
- Appraisal fee: $300 - $500
- Title insurance: $300 - $1000
- Closing costs: 2% - 5% of loan amount

Lock periods: 15 to 60 days to lock in your rate.',
    7200,
    TRUE,
    TRUE,
    15
);

-- Insert sample queries
INSERT INTO queries (document_id, question, answer, confidence, latency_ms, citations, support_details)
VALUES (
    (SELECT id FROM documents LIMIT 1),
    'What is the minimum credit score required?',
    'The minimum credit score required for mortgage refinancing is 620. However, a higher credit score (above 740) typically results in better interest rates and terms.',
    0.95,
    3450,
    '[{"sentence": "The minimum credit score required for mortgage refinancing is 620", "source_file": "sample1.txt", "similarity": 0.97}, {"sentence": "However, a higher credit score (above 740) typically results in better interest rates and terms", "source_file": "sample1.txt", "similarity": 0.92}]'::jsonb,
    '[{"sentence": "The minimum credit score required for mortgage refinancing is 620", "max_similarity": 0.97, "is_supported": true}, {"sentence": "However, a higher credit score (above 740) typically results in better interest rates and terms", "max_similarity": 0.92, "is_supported": true}]'::jsonb
);