# Building Large Language Models: From Foundations to Production

**A 9-Month Curriculum for Engineers Targeting Senior LLM / Applied-Research Roles**

---

## A Note Before You Start

I've spent a quarter-century in this field — from the kernel-methods era through deep learning to today's foundation models. Most "LLM courses" online are either too shallow (3-hour YouTube videos that teach you to call an API) or too academic (papers without working code). What follows is the curriculum I would design for a strong software engineer who wants to credibly claim "I can build and train large language models" on their CV and back it up in a technical interview.

Three honest things up front:

1. **You cannot train GPT-4 in your garage.** What you *can* do — and what will get you hired — is pre-train a 350M–1B parameter model from scratch end-to-end, fine-tune it, evaluate it rigorously, and explain every design decision. That is the bar.
2. **Budget realistically.** Plan for roughly $800–$2,000 in cloud compute for the capstone (Lambda Labs, RunPod, Modal, or spot instances on AWS). You can do a smaller version for under $300 if you're disciplined.
3. **Time commitment is real.** 15–20 hours per week for 8–9 months. Less than that and you're skimming; more and you'll burn out. The phases below assume this pace.

The course is organized into ten phases. Don't skip Phase 0 because you "already know Python" — the math gap is what separates people who pattern-match from people who can debug a training run.

---

## Curriculum Overview

| Phase | Title | Duration | Outcome |
|------:|-------|---------:|---------|
| 0 | Prerequisites & Math Foundations | 3 weeks | Comfortable with linear algebra, probability, autodiff |
| 1 | Deep Learning Foundations | 4 weeks | Implement MLPs, CNNs, RNNs from scratch in PyTorch |
| 2 | Classical NLP & Sequence Models | 3 weeks | Tokenization, embeddings, seq2seq, attention |
| 3 | The Transformer — Architecture Deep Dive | 4 weeks | Re-implement GPT-2 from scratch; understand every line |
| 4 | Pre-training Mechanics | 4 weeks | Data pipelines, mixed precision, distributed training |
| 5 | Scaling, Optimization & Systems | 3 weeks | Scaling laws, FlashAttention, ZeRO, FSDP |
| 6 | Post-training — SFT, RLHF, DPO | 4 weeks | Instruction-tune and align a model |
| 7 | Evaluation & Interpretability | 3 weeks | Build a rigorous eval harness |
| 8 | Inference, Serving & Deployment | 3 weeks | Quantization, vLLM, production serving |
| 9 | **Capstone Project** | 6–8 weeks | Train, align, evaluate, deploy a 350M–1B model |
| 10 | Interview Preparation | 2 weeks | System design, paper discussions, mock interviews |

**Total: ~36–38 weeks (~9 months) at 15–20 hours/week.**

---

## Phase 0 — Prerequisites & Math Foundations (3 weeks)

### Goals

You should be able to derive backprop on paper, explain why softmax-cross-entropy is numerically unstable in its naive form, and compute the gradient of a matrix-matrix product without flinching. If you can't, this phase is non-negotiable.

### Topics

**Week 1 — Linear Algebra**
Vectors, matrices, tensor operations. Matrix multiplication as composition of linear maps. Inner products, norms, projections. Eigendecomposition and SVD (you need SVD for understanding low-rank adaptation later). Matrix calculus — Jacobians and the chain rule on matrices.

**Week 2 — Probability & Statistics**
Random variables, expectation, variance. Joint, marginal, conditional distributions. KL divergence and cross-entropy (these *are* the loss function in language modeling — understand them deeply). Maximum likelihood estimation. The connection between MLE and cross-entropy loss is the single most important conceptual link in this entire curriculum.

**Week 3 — Optimization & Calculus**
Gradient descent and variants (SGD, momentum, Adam, AdamW). Why AdamW differs from Adam (decoupled weight decay — this matters for LLM training). Convex vs. non-convex optimization. Automatic differentiation: forward-mode vs. reverse-mode, and why deep learning uses reverse-mode.

### Resources

- **Book:** *Mathematics for Machine Learning* — Deisenroth, Faisal, Ong (free PDF online). Read Chapters 2–5 and 7.
- **Course:** Gilbert Strang's MIT 18.06 — Linear Algebra (the new "matrix methods" version, 18.065, is even better for ML).
- **Course:** 3Blue1Brown's *Essence of Linear Algebra* and *Essence of Calculus* on YouTube — watch these even if you think you don't need to. The geometric intuition pays off later.
- **Paper:** Kingma & Ba, "Adam: A Method for Stochastic Optimization" (2014). Read it. Then read the AdamW paper (Loshchilov & Hutter, 2017).

### Exercises

1. Implement backpropagation for a 3-layer MLP using only NumPy — no autograd. Verify gradients with finite differences.
2. Derive the gradient of softmax cross-entropy from scratch on paper and show why the combined form is numerically stable.
3. Implement Adam optimizer from scratch in NumPy and train it on a toy regression problem.

### Exit criteria

You can pick up any modern ML paper, see an equation like `L = -∑ y_i log(softmax(Wx)_i)`, and immediately know what its gradient with respect to W looks like.

---

## Phase 1 — Deep Learning Foundations (4 weeks)

### Goals

Move from math to working code. Build neural networks in PyTorch and understand the framework deeply enough that you're never confused by an error message.

### Topics

**Week 1 — PyTorch Fundamentals**
Tensors, broadcasting, the autograd engine. `nn.Module`, parameters, optimizers, the training loop. Common pitfalls: `model.train()` vs `model.eval()`, `optimizer.zero_grad()`, gradient accumulation. Build a simple MLP for MNIST and reach >97% accuracy.

**Week 2 — Convolutional Networks (briefly)**
You won't use CNNs much for LLMs, but they're foundational. Implement a small ResNet for CIFAR-10. The reason: residual connections are *the* architectural insight that made deep networks trainable, and they appear in every Transformer.

**Week 3 — Recurrent Networks**
Vanilla RNNs, the vanishing gradient problem (derive it), LSTM, GRU. Train a character-level RNN on Tiny Shakespeare. This is your last stop in pre-Transformer history — and it gives you the visceral feeling of why attention was such a leap.

**Week 4 — Regularization, Initialization, Normalization**
Weight initialization schemes (Xavier, He, and why they matter). Dropout. Batch normalization vs. layer normalization (LLMs use LayerNorm and increasingly RMSNorm — understand why). Gradient clipping. Learning rate schedules: warmup, cosine decay, linear decay.

### Resources

- **Course:** Andrej Karpathy's *Neural Networks: Zero to Hero* YouTube series. This is the single most important resource in this entire curriculum. Watch every video. Type every line of code yourself.
- **Book:** *Dive into Deep Learning* (d2l.ai) — free, code-first, excellent.
- **Documentation:** Read the PyTorch tutorials. All of them. Yes, all.
- **Paper:** "Deep Residual Learning for Image Recognition" (He et al., 2015). Understand why this works.

### Exercises

1. Implement an MLP, CNN, and LSTM in pure PyTorch (no `nn.Conv2d` shortcuts — write the convolution operation yourself at least once).
2. Reproduce a character-level RNN on Shakespeare. Generate text. Be amused at how bad it is. You'll appreciate Transformers more later.
3. Train ResNet-18 on CIFAR-10 to >90% accuracy without copying code.

### Exit criteria

PyTorch feels transparent. You can read someone's training script and immediately spot the bugs.

---

## Phase 2 — Classical NLP & Sequence Models (3 weeks)

### Goals

Understand the problem landscape that Transformers were invented to solve. You need this context to make informed architectural decisions later.

### Topics

**Week 1 — Tokenization & Embeddings**
Word-level, character-level, subword tokenization. BPE (Byte-Pair Encoding) — implement it from scratch. WordPiece, SentencePiece, Unigram. Why GPT uses BPE specifically. Word2Vec, GloVe — train them and look at the geometry of learned embeddings.

**Week 2 — Sequence-to-Sequence & Attention**
Encoder-decoder architectures. The original Bahdanau attention mechanism (2014) — this predates Transformers and is where attention was born. Implement seq2seq with attention for a small translation task (e.g., date-format conversion or English-to-French on a tiny corpus).

**Week 3 — Language Modeling as a Task**
Perplexity as a metric — derive its relationship to cross-entropy. N-gram models (yes, really — understand the baseline). The unreasonable effectiveness of next-token prediction. Why "predict the next token" turns out to be a sufficient objective for emergent capability.

### Resources

- **Book:** *Speech and Language Processing* by Jurafsky & Martin (3rd edition draft, free online). Chapters 2, 3, 6, 9, 10.
- **Course:** Stanford CS224N (Christopher Manning). Watch lectures 1–8 of the most recent year available on YouTube.
- **Paper:** Bahdanau, Cho, Bengio — "Neural Machine Translation by Jointly Learning to Align and Translate" (2014).
- **Paper:** Mikolov et al., "Efficient Estimation of Word Representations in Vector Space" (Word2Vec, 2013).

### Exercises

1. Implement BPE from scratch. Train it on a small corpus (Wikipedia dump, 100MB). Compare your vocabulary to the GPT-2 vocabulary.
2. Implement seq2seq with attention. Train on a date-normalization task ("July 4th, 1776" → "1776-07-04").
3. Train Word2Vec on a small corpus and visualize embeddings with t-SNE. Look for the famous "king - man + woman ≈ queen" relationship.

### Exit criteria

You can explain to a non-technical interviewer what tokenization is, why it matters, and walk through what BPE does step by step.

---

## Phase 3 — The Transformer: Architecture Deep Dive (4 weeks)

### Goals

This is the centerpiece of the entire curriculum. You will re-implement GPT-2 from scratch. By the end of this phase, you understand every tensor shape, every matrix multiplication, every design choice in a modern decoder-only Transformer.

### Topics

**Week 1 — The Original Transformer**
Read "Attention Is All You Need" three times. First for intuition, second for the math, third for the implementation details. Understand scaled dot-product attention. Multi-head attention — and why "multi-head" actually helps. Positional encodings (sinusoidal in the original; we'll get to RoPE later). Encoder-decoder vs. decoder-only.

**Week 2 — Implementing GPT-2 from Scratch**
Follow Karpathy's *Let's Build GPT* and *nanoGPT*. Implement:
- Token + positional embeddings
- Causal self-attention (with the triangular mask)
- Multi-head attention via tensor reshaping
- Feed-forward block (MLP with GELU)
- Pre-LayerNorm residual connections
- Weight tying between input and output embeddings
Then train it on Tiny Shakespeare. Then on OpenWebText (small subset).

**Week 3 — Modern Architectural Improvements**
The architecture has evolved since GPT-2. Study and implement:
- **RoPE** (Rotary Position Embeddings) — used in LLaMA, GPT-NeoX, most modern models
- **RMSNorm** instead of LayerNorm
- **SwiGLU** activation instead of GELU
- **Grouped Query Attention (GQA)** — the bridge between Multi-Head and Multi-Query
- **KV caching** for inference

**Week 4 — Mixture of Experts (briefly) & Variants**
MoE architectures — Mixtral, Switch Transformer, DeepSeek-MoE. You won't train one for the capstone, but you need to understand them conceptually. State-space models (Mamba, Mamba-2) — know they exist and the basic tradeoff vs. Transformers.

### Resources

- **Paper:** Vaswani et al., "Attention Is All You Need" (2017). The original.
- **Paper:** Radford et al., "Language Models are Unsupervised Multitask Learners" (GPT-2, 2019).
- **Paper:** Touvron et al., "LLaMA: Open and Efficient Foundation Language Models" (2023) — read carefully, it documents the modern architectural choices.
- **Code:** Karpathy's `nanoGPT` repo on GitHub. Read every line. Type it out.
- **Code:** Sebastian Raschka's *Build a Large Language Model from Scratch* (book + GitHub repo). Excellent companion to Karpathy's videos.
- **Blog:** Lilian Weng's "The Transformer Family" series. Comprehensive.
- **Blog:** Eleuther AI's "Transformer Math 101" — for understanding compute, memory, and parameter counts.

### Exercises

1. Implement GPT-2 from scratch in a single file (~300 lines). Train it to convergence on Tiny Shakespeare.
2. Replace LayerNorm with RMSNorm and benchmark. Replace sinusoidal positions with RoPE. Replace GELU MLP with SwiGLU. Re-train and compare.
3. Implement KV caching. Measure inference latency before and after. The speedup should be dramatic.
4. Take the original Transformer paper and reproduce Table 3 (parameter count breakdown) with your own implementation.

### Exit criteria

Given a whiteboard, you can draw the full architecture of a modern decoder-only LLM, label every tensor shape (batch, sequence, model dim, head dim), and explain the rationale behind every choice. This is interview-level fluency.

---

## Phase 4 — Pre-training Mechanics (4 weeks)

### Goals

Move from toy training runs to industrial-strength pre-training. Understand data pipelines, precision, distributed training, checkpointing, and the operational reality of large training jobs.

### Topics

**Week 1 — Data: The Most Underrated Topic**
Where pre-training data comes from: Common Crawl, FineWeb, RefinedWeb, The Pile, RedPajama, Dolma. Data quality filtering — heuristic rules, classifier-based filtering, deduplication (exact, MinHash, near-duplicate). Why "garbage in, garbage out" is the iron law of LLMs. The Chinchilla data-vs-parameters tradeoff. Implement a basic data filtering pipeline.

**Week 2 — Mixed Precision & Numerical Stability**
FP32 vs. FP16 vs. BF16 vs. FP8. Why BF16 dominates modern training (same exponent range as FP32). Gradient scaling for FP16. Loss spikes — what causes them, how to diagnose, when to skip steps. Implement mixed-precision training with `torch.cuda.amp`.

**Week 3 — Distributed Training: Data Parallelism**
DDP (Distributed Data Parallel) in PyTorch. How gradient all-reduce works. Why throughput doesn't scale linearly with GPUs. Effective batch size and learning rate scaling rules. Train a small model on 2–4 GPUs (rent if needed).

**Week 4 — Model & Pipeline Parallelism**
When DDP isn't enough: ZeRO (Stage 1, 2, 3), FSDP (Fully Sharded Data Parallel — PyTorch's native ZeRO-3). Tensor parallelism (Megatron-style). Pipeline parallelism. 3D parallelism. You probably won't use TP/PP for the capstone, but you need to explain them in interviews.

### Resources

- **Paper:** Hoffmann et al., "Training Compute-Optimal Large Language Models" (Chinchilla, 2022). Foundational for understanding data-vs-compute scaling.
- **Paper:** Penedo et al., "The RefinedWeb Dataset for Falcon LLM" (2023). Best practical reference on data filtering.
- **Paper:** Rajbhandari et al., "ZeRO: Memory Optimizations Toward Training Trillion Parameter Models" (2020).
- **Documentation:** PyTorch FSDP tutorial. Read it twice.
- **Blog:** Hugging Face's "The Ultra-Scale Playbook" — exceptional resource on distributed training.
- **Repo:** Karpathy's `llm.c` — pre-training in pure C/CUDA. Read for understanding what's actually happening at the metal.

### Exercises

1. Build a streaming data pipeline that reads from a tokenized binary file, packs sequences efficiently, and feeds a training loop without I/O bottlenecks.
2. Train the same model in FP32, FP16, and BF16. Compare loss curves, throughput, and final perplexity.
3. Run a training job on 2 GPUs with DDP, then with FSDP. Measure memory and throughput.
4. Implement a basic deduplication pipeline using MinHash on a small corpus.

### Exit criteria

You can spec out the data and compute requirements for training a model of arbitrary size, and explain the engineering tradeoffs at each scale.

---

## Phase 5 — Scaling, Optimization & Systems (3 weeks)

### Goals

Understand the systems-level concerns that separate hobbyist training from production. This is the area where most candidates fold in interviews.

### Topics

**Week 1 — Scaling Laws & Compute Planning**
Kaplan et al. (2020) original scaling laws. Chinchilla (2022) — why the Kaplan laws were wrong about data. The "20 tokens per parameter" rule of thumb. Compute budgets in FLOPs. Estimating training time: `6 × N × D` FLOPs where N=params, D=tokens. Practical calculation: given a budget of X GPU-hours, what model size and dataset size should you target?

**Week 2 — Attention Optimizations**
The O(n²) memory problem of vanilla attention. FlashAttention (v1, v2, v3) — understand IO-awareness as a design principle. PagedAttention (the idea behind vLLM). Multi-Query and Grouped-Query attention as memory optimizations during inference.

**Week 3 — Training Stability & Hyperparameters**
Learning rate: warmup, peak, decay schedules. The "muP" (maximal update parametrization) work — why hyperparameters transfer across scales. Gradient clipping. Loss spikes and recovery. Weight decay tuning. Batch size schedules. The role of the optimizer state in memory budgets (AdamW's 2x parameter overhead).

### Resources

- **Paper:** Kaplan et al., "Scaling Laws for Neural Language Models" (2020).
- **Paper:** Hoffmann et al., "Training Compute-Optimal Large Language Models" (Chinchilla, 2022) — read again, more carefully.
- **Paper:** Dao et al., "FlashAttention" and "FlashAttention-2" (2022, 2023).
- **Paper:** Yang et al., "Tensor Programs V: Tuning Large Neural Networks via Zero-Shot Hyperparameter Transfer" (μP, 2022).
- **Blog:** EleutherAI's "Transformer Math 101" and "Transformer Inference Arithmetic" (Carol Chen).

### Exercises

1. Given $1,000 and access to H100s at $2/hour, compute the optimal (Chinchilla-optimal) model size and dataset size. Show your math.
2. Implement FlashAttention's tiling logic in pure PyTorch (you won't beat the CUDA version, but the exercise teaches you the algorithm).
3. Run a learning-rate sweep across 3 model scales (10M, 50M, 200M params) and observe whether your best LR transfers.

### Exit criteria

You can answer "How big a model can I train with $5K?" within 10% accuracy and explain every term in your estimate.

---

## Phase 6 — Post-training: SFT, RLHF, DPO (4 weeks)

### Goals

Pre-trained models complete text. They don't follow instructions or behave helpfully. Post-training is what turns a base model into something like ChatGPT. This phase teaches the full alignment pipeline.

### Topics

**Week 1 — Supervised Fine-Tuning (SFT)**
Instruction datasets: Alpaca, Dolly, FLAN, ShareGPT, Open-Hermes, UltraChat. Chat templates and special tokens. Loss masking on the prompt vs. completing-only loss. Full fine-tuning vs. parameter-efficient methods. Catastrophic forgetting.

**Week 2 — Parameter-Efficient Fine-Tuning**
LoRA — derive why low-rank updates work and what rank to choose. QLoRA — 4-bit base model + LoRA adapters. Adapter tuning, prefix tuning, prompt tuning (for completeness — LoRA dominates in practice). When to use full fine-tuning vs. LoRA.

**Week 3 — RLHF: The Full Pipeline**
Reward modeling: collecting preference data, training a reward model on pairwise comparisons. The Bradley-Terry model. PPO (Proximal Policy Optimization) for language models. KL penalty against the SFT reference policy — and why it's essential. The reward hacking problem.

**Week 4 — DPO and the Modern Alternatives**
Direct Preference Optimization (DPO) — why it works without an explicit reward model. IPO, KTO, ORPO — newer variants and their tradeoffs. Constitutional AI and RLAIF (RL from AI feedback). When DPO suffices and when you still need PPO.

### Resources

- **Paper:** Ouyang et al., "Training Language Models to Follow Instructions with Human Feedback" (InstructGPT, 2022). The RLHF playbook.
- **Paper:** Rafailov et al., "Direct Preference Optimization" (DPO, 2023). Read three times.
- **Paper:** Hu et al., "LoRA: Low-Rank Adaptation of Large Language Models" (2021).
- **Paper:** Dettmers et al., "QLoRA: Efficient Finetuning of Quantized LLMs" (2023).
- **Paper:** Bai et al., "Constitutional AI" (Anthropic, 2022).
- **Code:** Hugging Face's `trl` (Transformer Reinforcement Learning) library — read the source.
- **Repo:** `axolotl` — production-grade fine-tuning framework. Use it.

### Exercises

1. SFT a small base model (e.g., Pythia-410M or TinyLlama-1.1B) on Alpaca-cleaned. Measure instruction-following quality before and after.
2. Apply LoRA fine-tuning to a 7B model on a single 24GB GPU (this is exactly why LoRA exists).
3. Train a reward model on a preference dataset (e.g., HH-RLHF subset). Verify it correctly ranks held-out pairs.
4. Run DPO on a small model end-to-end. Compare outputs to the SFT baseline.

### Exit criteria

Given a base model and a goal ("make it follow medical-domain instructions safely"), you can specify the full post-training pipeline, data requirements, and evaluation plan.

---

## Phase 7 — Evaluation & Interpretability (3 weeks)

### Goals

Evaluation is the most underrated skill in this field. Anyone can train a model. Few can tell you whether it's any good.

### Topics

**Week 1 — Standard Benchmarks**
MMLU, HellaSwag, ARC, TruthfulQA, GSM8K, MATH, HumanEval, BBH, IFEval, MT-Bench. What each measures, what each fails to measure. The contamination problem. Why benchmark scores are increasingly unreliable. Implement evaluation against MMLU using the standard 5-shot protocol.

**Week 2 — LLM-as-Judge & Human Evaluation**
Pairwise model comparisons. Arena-style evaluation (Chatbot Arena). MT-Bench with GPT-4 as judge — and its known biases (position bias, verbosity bias, self-preference). Building a rubric-based human eval. When automated metrics fail.

**Week 3 — Interpretability Primer**
Mechanistic interpretability — circuits, induction heads. Sparse autoencoders for feature extraction (Anthropic's recent work). Probing studies. Activation patching. You won't be doing original interp research, but you must speak the language.

### Resources

- **Tool:** `lm-evaluation-harness` from EleutherAI — the standard. Read the code and run it.
- **Paper:** Liang et al., "Holistic Evaluation of Language Models" (HELM, 2022).
- **Paper:** Zheng et al., "Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena" (2023).
- **Paper:** Olah et al. (Anthropic), "A Mathematical Framework for Transformer Circuits" (2021).
- **Paper:** Templeton et al. (Anthropic), "Scaling Monosemanticity" (2024).
- **Blog:** Hugging Face Open LLM Leaderboard methodology page.

### Exercises

1. Build a complete evaluation pipeline that runs your model against 5+ benchmarks and produces a single comparison table.
2. Implement LLM-as-judge for pairwise comparisons. Validate it against your own human judgments on 50 examples.
3. Find an induction head in a small Transformer using activation analysis.

### Exit criteria

You can design an evaluation suite for any LLM use case and justify every metric choice. You know when a benchmark number is meaningful and when it's noise.

---

## Phase 8 — Inference, Serving & Deployment (3 weeks)

### Goals

A model that can't be served cheaply at low latency is a research artifact. This phase makes you a full-stack LLM engineer.

### Topics

**Week 1 — Quantization**
INT8, INT4, GPTQ, AWQ, GGUF. The accuracy-vs-memory tradeoff at each precision level. Activation quantization vs. weight-only quantization. Practical use of `bitsandbytes` and `llama.cpp`. Run your fine-tuned model on a laptop CPU via GGUF.

**Week 2 — Serving Systems**
vLLM and PagedAttention. Continuous batching vs. static batching. TGI (Text Generation Inference). Speculative decoding. Prefix caching. Deploy your model behind an OpenAI-compatible API.

**Week 3 — Production Concerns**
Latency budgets: time-to-first-token (TTFT) vs. time-per-output-token (TPOT). Throughput vs. latency tradeoff. Cost per million tokens. Monitoring, logging, abuse mitigation, prompt injection defenses. Structured output (JSON mode, grammars).

### Resources

- **Paper:** Kwon et al., "Efficient Memory Management for Large Language Model Serving with PagedAttention" (vLLM, 2023).
- **Paper:** Frantar et al., "GPTQ: Accurate Post-Training Quantization for Generative Pre-trained Transformers" (2022).
- **Paper:** Lin et al., "AWQ: Activation-aware Weight Quantization" (2023).
- **Tool:** vLLM, TGI, llama.cpp — install and use all three.
- **Blog:** Anyscale's series on LLM serving economics.

### Exercises

1. Quantize your fine-tuned model to INT4 (AWQ) and measure the perplexity delta.
2. Serve your model with vLLM. Benchmark throughput at batch sizes 1, 8, 32. Plot the throughput-latency curve.
3. Convert your model to GGUF and run it on CPU. Time the tokens-per-second.

### Exit criteria

Given a model and a use case (chatbot, batch summarization, code completion), you can pick the right serving stack and predict the cost per million tokens to within 30%.

---

## Phase 9 — Capstone Project (6–8 weeks)

This is the project that goes on your resume. It is the project you will be asked about in every interview. Take it seriously.

### Project Title

**"Pre-training, Aligning, and Evaluating a 350M-Parameter Language Model from Scratch"**

(Adjust scale based on budget — see tiers below.)

### Three Tiers — Pick Based on Budget

| Tier | Model Size | Data Size | Approx. Compute Cost | Hardware |
|-----:|----------:|----------:|---------------------:|----------|
| Minimum | 124M (GPT-2 small) | 10B tokens | $200–400 | 1× A100 80GB for ~50 hours |
| **Recommended** | 350M | 20B tokens | $800–1,400 | 4× A100 80GB for ~30 hours |
| Standout | 1B–1.5B | 30B tokens | $2,000–3,500 | 8× A100 80GB for ~40 hours |

Use spot/preemptible instances. Lambda Labs, RunPod, Modal, Vast.ai, and TensorDock all offer competitive pricing. Your training script must support checkpoint resumption — instances will be preempted.

### Project Structure

**Phase A — Data (Week 1)**
- Download a curated pre-training corpus: FineWeb-Edu sample, SlimPajama, or RedPajama-V2 subset.
- Implement deduplication (MinHash) and quality filtering.
- Train a custom BPE tokenizer (32K vocab) on your data.
- Tokenize the full corpus into binary shards.
- Produce a clean data card: sources, filtering decisions, final token count, sample documents.

**Phase B — Architecture & Pre-training (Weeks 2–4)**
- Implement a modern decoder-only Transformer: RoPE positions, RMSNorm, SwiGLU MLP, GQA. Single file, ~500 lines.
- Configuration: 350M params (e.g., 24 layers, 1024 dim, 16 heads, 8 KV heads).
- Training: FSDP across GPUs, BF16 mixed precision, cosine LR schedule with warmup, gradient clipping at 1.0, AdamW (β1=0.9, β2=0.95).
- Log everything to Weights & Biases: loss, gradient norms, learning rate, throughput (tokens/sec/GPU), MFU (Model FLOPs Utilization).
- Target: Chinchilla-optimal token budget (~20× param count = 7B tokens minimum; aim for 20B+).
- Save checkpoints every 1B tokens. Resume gracefully from preemption.
- Document loss curves, hyperparameter choices, and at least one debugging incident (loss spike, NaN, OOM — you *will* hit one; document how you fixed it).

**Phase C — Post-training (Weeks 5–6)**
- SFT on a high-quality instruction mixture: UltraChat + OpenHermes-2.5 subset + a small curated set.
- Apply a proper chat template (ChatML or similar).
- DPO on a preference dataset (UltraFeedback or similar).
- Compare base, SFT, and DPO checkpoints qualitatively and quantitatively.

**Phase D — Evaluation (Week 7)**
- Run `lm-eval-harness` on a standard suite: MMLU (5-shot), HellaSwag, ARC-Easy/Challenge, TruthfulQA, GSM8K, IFEval.
- LLM-as-judge evaluation on MT-Bench against a 1B reference model (e.g., TinyLlama or Pythia-1B).
- Build a single comparison table: your base vs. your SFT vs. your DPO vs. comparable open models.
- Honest analysis: where does your model win, where does it lose, why?

**Phase E — Inference & Deployment (Week 8)**
- Quantize to INT4 with AWQ.
- Serve with vLLM behind a FastAPI endpoint with an OpenAI-compatible schema.
- Build a minimal web demo (Gradio or Streamlit).
- Measure: TTFT, throughput at varying batch sizes, cost per million tokens on your chosen hardware.

### Deliverables

1. **GitHub repository** — clean, well-documented, with reproducible training scripts. Include a README that walks through the entire pipeline.
2. **Technical report** (10–15 pages, PDF) — modeled on the LLaMA paper. Sections: Data, Architecture, Training, Post-training, Evaluation, Limitations, Future Work.
3. **Blog post** (3,000–5,000 words) — public, on Medium/Substack/your own site. Explain the project to a technically literate but non-expert audience.
4. **Model artifacts** — push base, SFT, and DPO checkpoints to Hugging Face Hub. Include the tokenizer, model card, and example usage.
5. **Demo** — a public link to your deployed model (Hugging Face Spaces is free).

### Resume Lines This Project Earns You

- "Pre-trained a 350M-parameter decoder-only Transformer from scratch on 20B tokens of filtered web data using FSDP across 4 A100 GPUs, achieving X perplexity and Y% MMLU."
- "Designed and implemented full post-training pipeline (SFT + DPO) using a custom preference dataset, improving instruction-following win-rate by Z% on MT-Bench."
- "Built end-to-end evaluation harness covering 6 standard benchmarks and LLM-as-judge methodology; published reproducible results in a technical report and open-sourced model weights."
- "Deployed quantized (INT4 AWQ) model via vLLM with sub-100ms TTFT and X tokens/sec throughput on commodity GPU."

### Interview Lines This Project Earns You

When asked "tell me about a challenging technical project," you have a 5-minute story with deep technical substance. When asked "how would you debug a loss spike in training," you have lived experience. When asked "explain DPO vs. PPO" — you've implemented both.

---

## Phase 10 — Interview Preparation (2 weeks)

### Topics

**Week 1 — Technical Depth**
Be ready to whiteboard:
- The full Transformer architecture with tensor shapes
- The math of self-attention (including the √d_k scaling — know why)
- Backpropagation through attention
- The KV cache and why it works
- LoRA math (low-rank decomposition)
- DPO loss derivation from the RLHF objective
- Chinchilla scaling laws — compute optimal point derivation
- Memory budget for training a model of size N (include optimizer state, gradients, activations)

**Week 2 — System Design & Behavioral**
Common LLM system design questions:
- "Design a code completion service serving 10K QPS."
- "Design a RAG system for a 100GB corporate document corpus."
- "How would you fine-tune a model for medical question answering?"
- "How would you evaluate a customer-support chatbot?"
- "Your model is hallucinating — walk me through how you'd diagnose and fix this."

Behavioral preparation around your capstone:
- The architectural decision you made and why
- The bug that took you longest to fix
- The result that surprised you
- What you'd do differently with 10× the compute

### Resources

- **Repo:** *llm-interview-questions* on GitHub (multiple good ones exist).
- **Blog:** Eugene Yan's writing on applied ML.
- **Blog:** Chip Huyen's "Designing Machine Learning Systems" book + her blog.
- **Practice:** Pramp, interviewing.io, or mock interviews with peers.

### Exit criteria

You can talk about LLMs for 90 minutes without running out of substance.

---

## Ongoing Habits (For the Rest of Your Career)

- **Read one paper per week.** Use the EleutherAI Discord, the Hugging Face daily papers, or the *Latent Space* podcast for filtering.
- **Reproduce one thing per month.** A paper, a blog post, a benchmark result.
- **Follow practitioners, not influencers.** On Twitter/X: Andrej Karpathy, Tri Dao, Stas Bekman, Sebastian Raschka, Aleksa Gordić, Eugene Yan, Lilian Weng (her blog), Jeremy Howard.
- **Contribute to one open-source repo.** `transformers`, `trl`, `vllm`, `axolotl`, `lm-evaluation-harness` all accept contributions.

---

## Final Words

A few things I wish someone had told me 25 years ago:

**The field rewards depth, not breadth, at the senior level.** Anyone can list a hundred papers. Few can derive attention's gradient on a whiteboard. Be the second person.

**Engineering matters more than people admit.** The "alchemy" of training LLMs is 80% data quality, infrastructure reliability, and disciplined experimentation. The clever architectural ideas are the visible 20%.

**Your capstone is your résumé.** Two engineers with identical formal qualifications walk into an interview. One has trained a model from scratch end-to-end, debugged a NaN at 3am, and published a model on Hugging Face. The other has read about all of it. Only one of them gets hired for senior roles. Be the first.

**The frontier moves fast — fundamentals don't.** New techniques will appear monthly. Attention, optimization, evaluation, distributed systems — these don't change. Master the fundamentals once; chase the frontier forever.

Good luck. Start with Phase 0 tomorrow. Don't perfect the plan — execute it.

---

*End of curriculum. Total study commitment: ~36–38 weeks at 15–20 hours/week.*
