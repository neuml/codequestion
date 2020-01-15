**StackExchange Query**

Models scored using Mean Reciprocal Rank (MRR)

| Model           | MRR   | 
| --------------- | :---: |
| SE 300d - BM25  | 71.0  |
| FastText - BM25 | 63.8  |
| ParaNMT - BM25  | 61.9  |
| TF-IDF          | 45.3  |
| BM25            | 43.6  |

**STS Benchmark**

Models scored using Pearson Correlation

| Model           | Supervision   | Dev   | Test  |
| --------------- | :-----------: | :---: | :---: |
| ParaNMT - BM25  | Train         | 82.6  | 78.1  |
| FastText - BM25 | Train         | 79.8  | 72.7  |
| SE 300d - BM25  | Train         | 77.2  | 70.4  |
