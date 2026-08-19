# Step-back prompting

Transforming a detailed question into a broader, high-level query to reduce the complexity of the vector search process making it easier for the model to identift relevant facts without getting bogged down by the specifics.

## Example
> which team did Thierry Audel play for from 2007 to 2008

Is broadened to

> which teams did Thierry Audel play for in his carreer

## System prompt
System prompt with [[Few-shot prompting]] examples.

> You are an expert at world knowledge. Your task is to step back and paraphrase a question to a more generic step-back question, which is easier to answer. Here are a few examples:
>
> input: could the members of the police perform lawful arrests?
> output: what can the members of the police do?
>
> input: Jan Sindel's was born in what country?
> output: what is Jan Sindel's personal history?
