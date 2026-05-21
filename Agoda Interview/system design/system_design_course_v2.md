# System Design by Building — A Hands-On Course

> A learn-by-doing curriculum for engineers preparing for system design interviews at deep-tech and big-tech companies. Every concept comes with an activity. By the end, you will have *built* the patterns you used to only read about — caches, load balancers, distributed counters, ML serving stacks, RAG systems, GPU-trained models, and a production-grade capstone.

---

## How This Course Works

**Who this is for.** You can write code in at least one language (Python is assumed in examples; Go and Rust are excellent alternatives). You have used a database. You have made an HTTP request. That's it. No prior system design knowledge required.

**The format of every concept.** Every idea in this course follows the same five-part pattern:

1. **The idea (in plain English).** What is this thing, with an analogy where helpful.
2. **Why it matters.** When you would reach for it, and what breaks if you don't.
3. **🛠️ Activity.** Something concrete you build, run, or measure. Has a time estimate, exact deliverable, and a "Done when…" success criterion.
4. **🤔 Reflect.** Two or three questions that test whether you actually understood it.
5. **⚠️ Common pitfalls.** The mistakes beginners and intermediates make.

**The cardinal rule.** *Do every activity.* Reading about a circuit breaker is worth zero. Building one that you can demonstrate triggering on a downstream failure is worth everything. Interviews reward people who can speak from experience; you build that experience here.

**How long this takes.** ~12–16 weeks of part-time study (~10 hours/week). You can compress to 6–8 weeks full-time. Faster than that and you are skipping activities — which defeats the point.

**Setup before you start.** Spend one evening installing these. You will use them throughout.

```
- A Unix-like shell (Linux, macOS, or WSL2 on Windows)
- Python 3.11+ and pip; optionally Go or Rust
- Docker Desktop (or Docker + docker-compose)
- A code editor (VS Code, Cursor, or your preference)
- git and a GitHub account
- A free Google Colab account (for GPU activities later)
- curl, jq, and httpie installed
```

You don't need a paid cloud account until Part 14 (LLM systems), and even then ~$50 of credits will cover everything.

---

# Table of Contents

- **Part 1.** What Even Is a System? (the mental model)
- **Part 2.** How Computers Talk — Networking from Scratch
- **Part 3.** Storing Things — Databases and Files
- **Part 4.** Doing Many Things at Once — Concurrency
- **Part 5.** One Server Isn't Enough — Scaling Basics
- **Part 6.** The Edge — Reverse Proxies, Load Balancers, CDNs
- **Part 7.** Caching — The Highest-Leverage Lever
- **Part 8.** Databases at Scale — Replication, Sharding, Indexes
- **Part 9.** Distributed Systems — Why It's Hard
- **Part 10.** Consensus and Coordination
- **Part 11.** Messaging — Queues, Logs, Streams
- **Part 12.** Data Pipelines — Batch and Stream
- **Part 13.** ML Systems — From Notebook to Production
- **Part 14.** ML at Scale — GPUs and Distributed Training
- **Part 15.** LLM Systems — RAG, Fine-Tuning, Serving
- **Part 16.** Observability — You Can't Fix What You Can't See
- **Part 17.** Reliability — Designing for Failure
- **Part 18.** Security Basics
- **Part 19.** Capstone Project — Document Intelligence Platform
- **Part 20.** Interview Frameworks and Communication
- **Part 21.** Mock Interview Bank with Self-Grading Rubric
- **Appendix A.** Numbers to Memorise
- **Appendix B.** Reading List
- **Appendix C.** A 14-Week Study Plan

---

# Part 1 — What Even Is a System?

## 1.1 Systems are made of parts that talk to each other

**The idea.** A "system" is two or more components that exchange information to accomplish something one component couldn't do alone. A web app is a *system* because the browser, the server, and the database collaborate. Your laptop is a *system* because the CPU, RAM, disk, and OS collaborate. The post office is a *system*: a sorting facility plus delivery vans plus mailboxes.

When we say "system design," we mean designing the *pieces*, the *connections* between pieces, and the *contracts* (what each piece promises to do).

**Why it matters.** Most beginner mistakes come from thinking about *one* piece in isolation. Senior engineers think in flows: a user click traverses a browser → a CDN → a load balancer → an API server → a cache → a database → and back. Every hop has latency, can fail, and costs money.

### 🛠️ Activity 1.1: Map a system you use every day (30 min)

Pick one: WhatsApp, Spotify, Uber, Gmail, Google Maps. On paper or in any drawing tool:

1. Draw the boxes for what you imagine the components are. Aim for 5–10 boxes.
2. Draw arrows for the data flow when *one specific user action* happens (sending a message, playing a song, requesting a ride).
3. For each arrow, write what data flows and roughly how big it is.
4. Mark which arrows go over the internet vs. inside a datacenter.

**Done when:** You have a labelled diagram and you can talk through your chosen action in 60 seconds.

**Compare with reality.** After drawing, search "How [WhatsApp / Spotify / Uber] works engineering blog" and read one. Note three things you missed.

### 🤔 Reflect

- Which of your boxes is most likely to be slow? Why?
- Which is most likely to fail? What happens to the user if it does?
- If your traffic 100×'d overnight, which box breaks first?

### ⚠️ Common pitfalls

- Drawing components without thinking about *what data flows where*.
- Treating boxes as magic ("the recommendation service") without thinking about what's inside.
- Forgetting failure modes — every connection between boxes can break.

---

## 1.2 Client and server, demystified

**The idea.** A *client* asks for things; a *server* provides them. The browser is a client; the web server is a server. But many programs are both: an API server is a client of a database server. There is nothing special about "server" software — it's just a program waiting in a loop for messages.

**Why it matters.** Once you internalise this, "the cloud" stops being magic. It's a lot of programs talking to each other.

### 🛠️ Activity 1.2: Build a Hello World client and server (45 min)

Create two Python files:

```python
# server.py
import socket

s = socket.socket()
s.bind(("127.0.0.1", 9000))
s.listen(5)
print("Server listening on port 9000...")

while True:
    conn, addr = s.accept()
    print(f"Connection from {addr}")
    data = conn.recv(1024).decode()
    print(f"Received: {data}")
    conn.sendall(f"Hello, you said: {data}".encode())
    conn.close()
```

```python
# client.py
import socket
import sys

s = socket.socket()
s.connect(("127.0.0.1", 9000))
s.sendall(sys.argv[1].encode())
print(s.recv(1024).decode())
s.close()
```

Run `python server.py` in one terminal, then `python client.py "hi there"` in another.

**Done when:** The server prints what the client sent, and the client prints the server's reply.

**Stretch:** Open *two* clients at the same time. What happens? (You'll see the server processes them one at a time. We'll fix that in Part 4.)

### 🤔 Reflect

- What happens if you run `python client.py "hi"` *before* starting the server?
- What happens if the server crashes while a client is mid-conversation?
- Why did we choose port 9000? What would happen if we chose port 80?

---

## 1.3 Latency, throughput, and why they aren't the same

**The idea.**
- **Latency** is *how long one thing takes*. A request takes 100 ms.
- **Throughput** is *how many things you can do per second*. The system handles 50,000 requests/sec.

A car analogy: a Ferrari has low latency (gets one passenger to the destination fast). A bus has high throughput (moves more passengers per hour) but higher latency per passenger.

**Why it matters.** In interviews, you must commit to *both numbers*, and you must understand that you can sometimes trade one for the other (batching, for example, sacrifices latency for throughput).

### 🛠️ Activity 1.3: Measure latency and throughput of your hello-world server (45 min)

1. Modify your server from 1.2 to handle requests in a loop without printing (printing is slow).
2. Write a simple `bench.py` that opens a connection, sends a message, reads the reply, closes — and times this in a loop of 1000 iterations.
3. Compute average latency (total time / 1000) and throughput (1000 / total time).
4. Now run *10 instances of `bench.py` in parallel*. Throughput should not 10×, because your server is single-threaded. Note the actual numbers.

**Done when:** You have four numbers written down: serial latency, serial throughput, parallel latency, parallel throughput — and you can explain why parallel throughput barely improved.

### 🤔 Reflect

- Where is the time *actually* going? (Hint: it's almost entirely the TCP connect/close.)
- If you reused one connection for all 1000 iterations, how much faster would it be? (Try it.)
- What if the server had a 50 ms delay per request — what would average latency become with 10 parallel clients?

### ⚠️ Common pitfalls

- Quoting average latency only. Always think about p50, p95, p99 (we'll get there).
- Confusing latency with throughput. They are independent dimensions.

---

## 1.4 Back-of-envelope estimation

**The idea.** Before designing anything, estimate the load. Numbers tell you whether you need one server or a thousand.

**Why it matters.** Most bad designs come from skipping this step. Estimation also signals seniority in interviews — it shows you reason from first principles.

**The numbers you'll use repeatedly:**
- 1 byte = 1, 1 KB ≈ 10³, 1 MB ≈ 10⁶, 1 GB ≈ 10⁹, 1 TB ≈ 10¹², 1 PB ≈ 10¹⁵.
- 1 day = 86,400 seconds (round to 100,000 in interviews).
- DAU (Daily Active Users) is typically 10–30% of MAU.
- A request usually takes ~1 KB in, ~1–10 KB out.
- 1 server can handle ~10,000–50,000 simple HTTP req/s. Database writes are 10–100× slower.

### 🛠️ Activity 1.4: Estimate three real systems (60 min)

For each of these, write down: total users, DAU, write QPS, read QPS, total storage/year, peak bandwidth.

1. **A new chat app** with 50M MAU. Average user sends 30 messages/day, reads 200.
2. **A video site** like YouTube. 2B MAU, 500M DAU. Each DAU watches 30 min/day at 5 Mbps average.
3. **A ride-sharing app** like Uber. 100M MAU, 30M DAU. Each user opens the app 3 times/day. Each open polls driver locations every 4 seconds for 2 minutes. Each ride generates ~1KB of route data.

**Done when:** You have a worksheet with all three estimates and you can defend each number in one sentence.

**Check yourself.** YouTube actually serves ~1 billion hours/day. Did you get within 2× of the right order of magnitude? That's good enough — being within 10× is the interview bar.

### 🤔 Reflect

- For YouTube, where does the bandwidth bill go — the database or the CDN?
- For Uber, the *peak* QPS for driver-location polling matters more than average. Why?
- What's the difference between "100M total users" and "100M concurrent users"? Why does it matter?

---

# Part 2 — How Computers Talk: Networking from Scratch

You don't need to be a network engineer, but you need a working mental model. Most "weird bugs" in distributed systems are network bugs in disguise.

## 2.1 IP addresses, ports, and DNS

**The idea.** Every computer on a network has an *IP address* (like a street address). Each running program listens on a *port* (like an apartment number). DNS is the phone book that maps human-readable names like `google.com` to IP addresses.

**Why it matters.** Most production failures look like "the service is down" but are actually "DNS is slow" or "the wrong port is open" or "this region's IP can't reach that region's IP."

### 🛠️ Activity 2.1: Explore networks with built-in tools (30 min)

Run each and observe:

```bash
# What's my computer's IP?
ifconfig    # macOS / Linux
ipconfig    # Windows

# How does the internet route to google.com?
traceroute google.com   # macOS / Linux
tracert google.com      # Windows

# What's google.com's actual IP?
dig google.com +short
# or: nslookup google.com

# How fast is the round trip?
ping -c 5 google.com

# What happens at TCP/HTTP level?
curl -v https://example.com
```

**Done when:** You can answer: how many hops between you and `google.com`? What is `example.com`'s IP today? What's your DNS resolver's address?

### 🤔 Reflect

- Why do `dig google.com` queries from different parts of the world return different IPs? (Hint: GeoDNS.)
- If `traceroute` shows 15 hops, and each hop adds ~5 ms, what's the minimum possible RTT?
- Why does the *first* HTTP request to a site often feel slower than the second? (Hint: DNS caching, TCP, TLS.)

---

## 2.2 TCP vs UDP

**The idea.**
- **TCP** is a phone call. There's a "hello, can you hear me?" handshake. The line stays open. Bytes arrive in order. If something is missed, it's resent. Reliable but with overhead.
- **UDP** is a postcard. You drop it in the mail. Maybe it arrives, maybe not, maybe out of order. Fast and cheap but lossy.

**Why it matters.** TCP is the default for almost everything (HTTP, gRPC, databases). UDP is for video/voice calls (where slight loss is OK and latency matters), DNS, and the *new* HTTP/3 (which is built on QUIC, which is on UDP — for good reasons we'll see).

### 🛠️ Activity 2.2: See TCP and UDP in action (45 min)

In one terminal, run a "TCP listener":
```bash
nc -l 9001    # listens on port 9001 (TCP by default)
```

In another, connect:
```bash
nc 127.0.0.1 9001
```

Type messages — they appear in the other terminal. Now Ctrl-C the *server*. The client gets disconnected.

Now do the same with UDP:
```bash
# Server
nc -u -l 9002

# Client
nc -u 127.0.0.1 9002
```

Send messages. Now Ctrl-C the server and *keep typing* in the client. Notice: the client doesn't even know.

**Done when:** You can explain in one sentence why TCP knows when the other side disappears and UDP doesn't.

### 🤔 Reflect

- For a video call, is occasional packet loss tolerable? Is delayed retransmission tolerable?
- For a bank transfer, which protocol would you build on? Why?

---

## 2.3 HTTP — the protocol that runs the web

**The idea.** HTTP is a *request-response* text protocol over TCP. The client sends:

```
GET /users/42 HTTP/1.1
Host: api.example.com
Authorization: Bearer xxx

```

The server replies:

```
HTTP/1.1 200 OK
Content-Type: application/json
Content-Length: 32

{"id": 42, "name": "Rishin"}
```

That's it. Verbs (GET, POST, PUT, DELETE, PATCH), status codes (2xx success, 3xx redirect, 4xx client error, 5xx server error), headers (metadata), body (the data).

**Why it matters.** Everything you'll touch — REST APIs, GraphQL, gRPC's underlying protocol, webhooks — is HTTP or HTTP-shaped.

### 🛠️ Activity 2.3a: Speak HTTP by hand (20 min)

```bash
# Connect to a real server with raw TCP
nc example.com 80
```

Then type these lines and press Enter twice at the end:
```
GET / HTTP/1.1
Host: example.com

```

You'll see the raw HTTP response come back. **Congratulations — you're now a web browser.**

### 🛠️ Activity 2.3b: Build a tiny HTTP server (90 min)

Don't use a framework. Build directly on sockets:

```python
# tiny_http.py
import socket

def handle(conn):
    data = conn.recv(4096).decode()
    request_line = data.split("\r\n")[0]
    method, path, _ = request_line.split(" ")
    
    if path == "/":
        body = "Hello!"
        status = "200 OK"
    elif path == "/time":
        from datetime import datetime
        body = str(datetime.now())
        status = "200 OK"
    else:
        body = "Not Found"
        status = "404 Not Found"
    
    response = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Content-Type: text/plain\r\n"
        f"\r\n"
        f"{body}"
    )
    conn.sendall(response.encode())
    conn.close()

s = socket.socket()
s.bind(("127.0.0.1", 8080))
s.listen(5)
while True:
    conn, _ = s.accept()
    handle(conn)
```

Run it; visit `http://localhost:8080/` and `http://localhost:8080/time` in your browser.

**Done when:** You can explain every line. Then add a `/echo?msg=hello` endpoint that returns the query parameter.

### 🤔 Reflect

- Why does HTTP need `Content-Length`? What happens without it?
- Why are headers separated by `\r\n` and the body by `\r\n\r\n` (a blank line)?
- What's the difference between PUT and POST, *philosophically*?

### ⚠️ Common pitfalls

- Forgetting that HTTP is *stateless* — the server forgets you between requests unless you send a cookie or token.
- Confusing `404` (resource doesn't exist) with `403` (you can't see it) with `401` (you didn't auth).

---

## 2.4 HTTP/1.1, HTTP/2, HTTP/3 — what changed and why

**The idea.**
- **HTTP/1.1**: One request at a time per connection (head-of-line blocking). Workaround: open many connections.
- **HTTP/2**: Multiple requests *multiplexed* on one connection. Binary, faster headers (HPACK).
- **HTTP/3**: Same multiplexing, but built on UDP+QUIC, removing TCP head-of-line blocking, and with faster handshakes.

**Why it matters.** When designing a mobile app on a flaky cellular network, HTTP/3 is dramatically better. When designing a service-to-service API in a datacenter, gRPC over HTTP/2 is the default.

### 🛠️ Activity 2.4: See the difference (30 min)

```bash
# Time a request to a site that supports HTTP/2 and HTTP/3
curl -w "Connect: %{time_connect}s, TTFB: %{time_starttransfer}s, Total: %{time_total}s\n" \
     -o /dev/null -s https://www.cloudflare.com
     
# Force HTTP/2
curl --http2 -o /dev/null -s -w "%{http_version}\n" https://www.cloudflare.com

# Force HTTP/1.1
curl --http1.1 -o /dev/null -s -w "%{http_version}\n" https://www.cloudflare.com
```

**Done when:** You can list one practical advantage of each version.

---

## 2.5 TLS in 60 seconds

**The idea.** TLS makes HTTP into HTTPS by adding encryption + authentication + integrity. The handshake exchanges keys; then everything is encrypted. Certificates prove identity (signed by a Certificate Authority your OS trusts).

**Why it matters.** Every production API is HTTPS. Misconfigured TLS is a top-3 source of outages. Self-signed certs in dev are normal; trusting them in prod is a vulnerability.

### 🛠️ Activity 2.5: Inspect a TLS handshake (30 min)

```bash
# See the cert and handshake
openssl s_client -connect example.com:443 -servername example.com < /dev/null

# Time just the TLS handshake
curl -w "TLS handshake: %{time_appconnect}s\n" -o /dev/null -s https://example.com
```

**Done when:** You can identify the certificate's issuer, expiry date, and the cipher suite used.

---

# Part 3 — Storing Things: Databases and Files

## 3.1 Memory, disk, and the speed gap

**The idea.** RAM is fast (~100 ns/access) but volatile (loses everything on power loss) and expensive. Disks (SSD/HDD) are slow (~10 µs to ~10 ms) but durable and cheap. Modern systems use both: hot data in RAM, cold data on disk.

**Why it matters.** "Just put it in memory" is sometimes correct (Redis), sometimes catastrophic (your e-commerce orders). Knowing the trade-off is foundational.

### 🛠️ Activity 3.1: Measure the memory–disk speed gap (30 min)

```python
# bench.py
import time

# Memory: write 1M ints to a list
start = time.perf_counter()
data = [i for i in range(1_000_000)]
print(f"Memory write 1M: {time.perf_counter()-start:.3f}s")

# Disk: write 1M lines to a file
start = time.perf_counter()
with open("data.txt", "w") as f:
    for i in range(1_000_000):
        f.write(f"{i}\n")
print(f"Disk write 1M: {time.perf_counter()-start:.3f}s")

# Disk + fsync (force to disk, no OS buffer)
import os
start = time.perf_counter()
with open("data.txt", "w") as f:
    for i in range(1_000_000):
        f.write(f"{i}\n")
    f.flush()
    os.fsync(f.fileno())
print(f"Disk+fsync 1M: {time.perf_counter()-start:.3f}s")
```

**Done when:** You see disk is significantly slower than memory, and `fsync` is dramatically slower still. Write down a one-line takeaway.

### 🤔 Reflect

- Databases must `fsync` on commit (otherwise crashes lose data). Why does this make them ~100× slower than memory?
- Why does Redis (in-memory database) recommend "AOF every-second" instead of "AOF on every write"?

---

## 3.2 Build a key-value store from scratch

**The idea.** A database is, at its core, a program that stores key→value pairs durably and lets you read them back. Real databases add transactions, indexes, replication, and a query language — but the core is simple.

### 🛠️ Activity 3.2a: A naive KV store (60 min)

```python
# kv_naive.py
import json, os

class KV:
    def __init__(self, path="db.json"):
        self.path = path
        self.data = {}
        if os.path.exists(path):
            with open(path) as f:
                self.data = json.load(f)
    
    def get(self, key):
        return self.data.get(key)
    
    def put(self, key, value):
        self.data[key] = value
        # Persist on every write
        with open(self.path, "w") as f:
            json.dump(self.data, f)
    
    def delete(self, key):
        self.data.pop(key, None)
        with open(self.path, "w") as f:
            json.dump(self.data, f)

if __name__ == "__main__":
    kv = KV()
    kv.put("name", "Rishin")
    kv.put("city", "Delhi")
    print(kv.get("name"))
```

**Done when:** It works across restarts (close Python, restart, `get` returns the value).

### 🛠️ Activity 3.2b: An append-only log KV store (90 min)

The naive version rewrites the entire file on every write. Real databases (RocksDB, LevelDB, the storage engine inside Cassandra) use *append-only logs* + indexes. Here's the simplest version:

```python
# kv_log.py
import os

class LogKV:
    def __init__(self, path="db.log"):
        self.path = path
        self.index = {}  # in-memory: key -> file offset
        if os.path.exists(path):
            self._rebuild_index()
    
    def _rebuild_index(self):
        with open(self.path, "rb") as f:
            offset = 0
            while True:
                line = f.readline()
                if not line:
                    break
                # format: "PUT key value\n" or "DEL key\n"
                parts = line.decode().rstrip().split(" ", 2)
                if parts[0] == "PUT":
                    self.index[parts[1]] = offset
                elif parts[0] == "DEL":
                    self.index.pop(parts[1], None)
                offset = f.tell()
    
    def put(self, key, value):
        with open(self.path, "ab") as f:
            offset = f.tell()
            f.write(f"PUT {key} {value}\n".encode())
            f.flush()
            os.fsync(f.fileno())
            self.index[key] = offset
    
    def get(self, key):
        if key not in self.index:
            return None
        with open(self.path, "rb") as f:
            f.seek(self.index[key])
            line = f.readline().decode().rstrip()
            return line.split(" ", 2)[2]
    
    def delete(self, key):
        with open(self.path, "ab") as f:
            f.write(f"DEL {key}\n".encode())
            f.flush()
            os.fsync(f.fileno())
        self.index.pop(key, None)
```

**Done when:** It works *and* you understand:
- Why writes are O(1) and don't slow down as the DB grows.
- Why the file grows forever even if you delete things (this is why real DBs do *compaction*).
- Why `fsync` matters (kill -9 your process mid-write and verify nothing is lost).

### 🤔 Reflect

- Real-world LSM-tree databases (RocksDB, Cassandra) use this exact pattern. Why is it called "log-structured"?
- What's the trade-off vs. the naive version's "rewrite everything"?
- How would you implement *range queries* (`get all keys between A and Z`) on this?

### ⚠️ Common pitfalls

- Forgetting `fsync` and assuming the data is durable.
- Writing the index to disk on every operation (defeats the point — keep it in memory, rebuild on startup).

---

## 3.3 SQL and ACID

**The idea.** SQL is the lingua franca for relational databases. ACID is the contract:

- **A**tomicity: a transaction is all-or-nothing.
- **C**onsistency: a transaction takes the DB from one valid state to another.
- **I**solation: concurrent transactions don't see each other's intermediate state.
- **D**urability: once committed, it's safe even on crash.

**Why it matters.** Most "we'll add a NoSQL store for performance" decisions later need ACID and have to be rebuilt. Knowing what ACID *gives* you and what it *costs* you is foundational.

### 🛠️ Activity 3.3a: SQLite from scratch (45 min)

SQLite is a real, production-grade database in a single file with no setup. Use it.

```python
# bank.py
import sqlite3

con = sqlite3.connect("bank.db")
con.execute("""
CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY,
    owner TEXT,
    balance REAL
)""")
con.execute("DELETE FROM accounts")  # reset for demo
con.execute("INSERT INTO accounts VALUES (1, 'Alice', 100)")
con.execute("INSERT INTO accounts VALUES (2, 'Bob', 100)")
con.commit()

# Transfer $30 from Alice to Bob - WITHOUT a transaction
con.execute("UPDATE accounts SET balance = balance - 30 WHERE id=1")
# Imagine the program crashes here
con.execute("UPDATE accounts SET balance = balance + 30 WHERE id=2")
con.commit()

for row in con.execute("SELECT * FROM accounts"):
    print(row)
```

Now run it again, but this time *intentionally raise an exception* between the two updates. Observe Alice loses $30 and Bob never gets it. This is what ACID prevents.

### 🛠️ Activity 3.3b: Transactions (30 min)

Wrap it properly:

```python
try:
    con.execute("BEGIN")
    con.execute("UPDATE accounts SET balance = balance - 30 WHERE id=1")
    raise Exception("simulated crash")
    con.execute("UPDATE accounts SET balance = balance + 30 WHERE id=2")
    con.execute("COMMIT")
except Exception as e:
    con.execute("ROLLBACK")
    print(f"Transaction failed: {e}")

for row in con.execute("SELECT * FROM accounts"):
    print(row)
```

**Done when:** You see that the rollback restored Alice's balance, even though we raised an exception mid-transaction.

### 🤔 Reflect

- What does ACID's "I" (isolation) mean if two transactions hit the database at exactly the same moment?
- The default SQLite isolation level is "serializable." What does that mean in plain English?

---

## 3.4 Indexes, or "why your queries are slow"

**The idea.** Without an index, the database scans every row to answer your query. With an index (a B-tree, almost always), it can find the relevant rows in O(log N). Indexes speed up reads but slow down writes (because the index must also be updated).

### 🛠️ Activity 3.4: Demonstrate the difference (45 min)

```python
import sqlite3, time, random

con = sqlite3.connect(":memory:")
con.execute("CREATE TABLE users (id INTEGER, email TEXT, name TEXT)")

# Insert 1M rows
print("Inserting 1M rows...")
con.executemany(
    "INSERT INTO users VALUES (?, ?, ?)",
    [(i, f"user{i}@x.com", f"User {i}") for i in range(1_000_000)]
)
con.commit()

# Query without index
target = f"user{random.randint(0, 999999)}@x.com"
start = time.perf_counter()
list(con.execute("SELECT * FROM users WHERE email = ?", (target,)))
print(f"Without index: {(time.perf_counter()-start)*1000:.1f} ms")

# Add index
con.execute("CREATE INDEX idx_email ON users(email)")
start = time.perf_counter()
list(con.execute("SELECT * FROM users WHERE email = ?", (target,)))
print(f"With index: {(time.perf_counter()-start)*1000:.1f} ms")
```

**Done when:** You see the indexed query is hundreds of times faster, and you can explain why.

### 🤔 Reflect

- If you index *every column*, queries are fast — but writes become slow. Why?
- Composite indexes: `INDEX(country, city)` can serve `WHERE country = 'IN'` but not `WHERE city = 'Delhi'`. Why?
- What's an index on a column where every row has the same value? (Useless — high *cardinality* matters.)

### ⚠️ Common pitfalls

- Adding indexes "just in case" — they cost storage and write throughput.
- Indexing a column you query with `LIKE '%foo%'` — most B-tree indexes can't help with leading-wildcard searches.

---

## 3.5 SQL vs NoSQL — when to choose what

**The idea.** "NoSQL" is a marketing term covering several different things:

- **Key-value** (Redis, DynamoDB): blazing-fast point lookups by key. Bad for queries that aren't "give me this key."
- **Document** (MongoDB): JSON-shaped, flexible schema, secondary indexes possible.
- **Wide-column** (Cassandra, HBase): many columns per row, sparse, optimised for write-heavy time-series.
- **Graph** (Neo4j): edges as first-class citizens. Good for "friends of friends."

**Why it matters.** Pick the database from the *access pattern*, not from team familiarity. The number-one design mistake is "we'll use Mongo because it's flexible" without understanding the access pattern.

### 🛠️ Activity 3.5: Same data, two databases (90 min)

Pick a small dataset (e.g. movies + ratings — grab MovieLens 100K).

1. Load it into Postgres. Write SQL to answer: top-10 highest-rated movies; user X's average rating; movies similar to X (joined via genres).
2. Load *the same data* into Redis. Now answer the same questions.

You'll quickly find Redis is awesome for "user X's rating list" (one key, one operation) and terrible for joins. Postgres is fine for both but slower for the simple lookup.

**Done when:** You can articulate when you'd reach for which, with one example each.

### 🤔 Reflect

- Why does Redis force you to think about access patterns *before* loading data?
- If you wanted "all movies with a 5-star rating from any user," what would each DB do?

---

# Part 4 — Doing Many Things at Once: Concurrency

## 4.1 Concurrency vs parallelism

**The idea.**
- **Concurrency**: dealing with many things at once (one chef juggling 5 dishes by switching between them).
- **Parallelism**: doing many things at once (5 chefs, each cooking one dish).

A single CPU core can be concurrent (via context switching) but not parallel. Multi-core machines can be both.

**Why it matters.** The Hello World server in Part 1 was concurrent-incapable: while it talked to client A, client B waited. Real servers must be concurrent.

### 🛠️ Activity 4.1: Make your server concurrent (60 min)

Take `server.py` from Activity 1.2 and make it handle multiple clients simultaneously by spawning a thread per connection:

```python
import socket, threading

def handle(conn, addr):
    print(f"Handling {addr}")
    data = conn.recv(1024).decode()
    # Simulate work
    import time; time.sleep(2)
    conn.sendall(f"Hello, you said: {data}".encode())
    conn.close()

s = socket.socket()
s.bind(("127.0.0.1", 9000))
s.listen(5)
while True:
    conn, addr = s.accept()
    threading.Thread(target=handle, args=(conn, addr), daemon=True).start()
```

Connect with two clients within 2 seconds; both should get responses around the same time, not 2 seconds apart.

**Done when:** Two clients are served in parallel; if you start a third while two are mid-flight, all three finish around the same time.

### 🤔 Reflect

- What happens with 10,000 concurrent clients in this design? (Hint: you can't have 10,000 OS threads cheaply.)
- What if `handle` does a CPU-heavy task (like image compression)? Will threads help in Python? (Hint: GIL.)

---

## 4.2 Race conditions and locks

**The idea.** When multiple threads modify the same data without coordination, they race. The result depends on *timing* — i.e. it's non-deterministic. Locks (mutexes) prevent this by allowing only one thread into a "critical section" at a time.

**Why it matters.** Race conditions cause some of the most frustrating bugs in software. They're hard to reproduce, hard to debug, and a senior engineer must spot them on sight.

### 🛠️ Activity 4.2a: Reproduce a race condition (30 min)

```python
import threading

counter = 0

def increment():
    global counter
    for _ in range(100_000):
        counter += 1

threads = [threading.Thread(target=increment) for _ in range(10)]
for t in threads: t.start()
for t in threads: t.join()

print(f"Counter is {counter}, expected {10 * 100_000}")
```

Run it a few times. You may get the right answer (Python's GIL helps) — try with `multiprocessing` and shared memory, or repeat with smaller increments and see drift. Or run this in Go to see the race clearly:

```go
package main
import ("fmt"; "sync")

func main() {
    counter := 0
    var wg sync.WaitGroup
    for i := 0; i < 10; i++ {
        wg.Add(1)
        go func() {
            defer wg.Done()
            for j := 0; j < 100_000; j++ {
                counter++
            }
        }()
    }
    wg.Wait()
    fmt.Printf("counter = %d (expected %d)\n", counter, 1_000_000)
}
```

Go reliably shows lost updates. Run with `go run -race main.go` — it explicitly flags the data race.

### 🛠️ Activity 4.2b: Fix it with a lock (30 min)

```python
import threading

counter = 0
lock = threading.Lock()

def increment():
    global counter
    for _ in range(100_000):
        with lock:
            counter += 1
```

Now it's correct. **But it's slower.** Time both versions.

**Done when:** You've measured the lock's overhead and you can explain *why* it makes things slower (serialisation of work that was previously parallel).

### 🤔 Reflect

- A lock is the simplest way to make a critical section safe. What does it cost?
- If two threads each need lock A and lock B, what can go wrong if they acquire them in different orders? (Deadlock.)

### ⚠️ Common pitfalls

- Locking too coarsely (one giant lock around everything) — kills parallelism.
- Locking too finely — easy to forget a critical section, easy to deadlock.
- Forgetting that *any* shared mutable state needs synchronisation, not just `int`s.

---

## 4.3 Async I/O

**The idea.** When a thread is blocked waiting for I/O (network, disk), it's not doing anything useful. Async I/O lets *one thread* handle thousands of concurrent connections by switching between them whenever one blocks. Implemented as event loops (Python `asyncio`, Node.js, Tokio, Go runtime under the hood).

**Why it matters.** For *I/O-bound* work, async is dramatically more efficient than threads. For *CPU-bound* work, async doesn't help — you need real parallelism (multiple processes / cores).

### 🛠️ Activity 4.3: Build an async HTTP fetcher (60 min)

Compare three implementations of "fetch 100 URLs":

```python
# Version 1: Sequential (slow)
import requests, time
urls = ["https://httpbin.org/delay/1"] * 50
start = time.perf_counter()
for u in urls:
    requests.get(u)
print(f"Sequential: {time.perf_counter()-start:.1f}s")

# Version 2: Threads
from concurrent.futures import ThreadPoolExecutor
start = time.perf_counter()
with ThreadPoolExecutor(max_workers=50) as ex:
    list(ex.map(requests.get, urls))
print(f"Threads: {time.perf_counter()-start:.1f}s")

# Version 3: Async
import asyncio, aiohttp
async def fetch_all():
    async with aiohttp.ClientSession() as s:
        await asyncio.gather(*(s.get(u) for u in urls))
start = time.perf_counter()
asyncio.run(fetch_all())
print(f"Async: {time.perf_counter()-start:.1f}s")
```

**Done when:** Sequential is ~50 s; threads and async are both ~1–2 s. You understand both *can* be efficient for I/O, but async scales to higher concurrency for less memory.

### 🤔 Reflect

- Which version uses fewer OS resources? Why does that matter at 100K concurrent connections?
- If `fetch` did a CPU-heavy parse on each result, would async still win?

---

## 4.4 Producer-consumer and bounded queues

**The idea.** A common pattern: one set of workers *produces* items (e.g. requests, events), another *consumes* them (e.g. processes, stores). A *bounded queue* between them provides backpressure: if consumers can't keep up, the queue fills, and the queue blocks producers.

**Why it matters.** Almost every production data pipeline uses this pattern. Unbounded queues are an outage waiting to happen — they consume memory until OOM.

### 🛠️ Activity 4.4: Build a producer-consumer pipeline (60 min)

```python
import queue, threading, time, random

q = queue.Queue(maxsize=10)  # bounded!

def producer():
    for i in range(50):
        q.put(i)  # blocks if queue is full
        print(f"  produced {i}, queue size = {q.qsize()}")
        time.sleep(random.uniform(0, 0.1))

def consumer(name):
    while True:
        item = q.get()
        print(f"{name} consumed {item}")
        time.sleep(random.uniform(0.1, 0.5))  # slow!
        q.task_done()

threading.Thread(target=producer).start()
threading.Thread(target=consumer, args=("C1",), daemon=True).start()
threading.Thread(target=consumer, args=("C2",), daemon=True).start()

q.join()  # wait for all items processed
```

Watch the queue fill up; producers block; the system finds equilibrium.

**Done when:** You see backpressure in action — the producer slows down because the queue is full.

### 🤔 Reflect

- What if `q` were unbounded and the producer ran 1,000,000 items? (RAM exhaustion.)
- What if you make the queue size 1? (Producer and consumer become tightly coupled — same as no queue.)
- How would you handle queue-full as "drop oldest" vs "drop newest" vs "block"?

### ⚠️ Common pitfalls

- Unbounded queues "for safety" — they convert a small problem into an OOM crash.
- Forgetting `task_done()` and `join()` — the program exits before processing finishes.

---

## 4.5 Deadlock — and how to spot it

**The idea.** Deadlock: thread A holds lock 1 and waits for lock 2; thread B holds lock 2 and waits for lock 1. Both wait forever.

### 🛠️ Activity 4.5: Cause a deadlock, then fix it (45 min)

```python
import threading, time

lock_a = threading.Lock()
lock_b = threading.Lock()

def task1():
    with lock_a:
        time.sleep(0.1)
        with lock_b:
            print("task1 done")

def task2():
    with lock_b:
        time.sleep(0.1)
        with lock_a:
            print("task2 done")

t1 = threading.Thread(target=task1)
t2 = threading.Thread(target=task2)
t1.start(); t2.start()
t1.join(timeout=2); t2.join(timeout=2)
print("done" if not t1.is_alive() else "DEADLOCKED")
```

**Fix:** always acquire locks in the same global order (e.g. `lock_a` before `lock_b`).

**Done when:** You can both reproduce and prevent the deadlock, and you understand the rule: *consistent lock ordering*.

---

# Part 5 — One Server Isn't Enough: Scaling Basics

## 5.1 Vertical vs horizontal scaling

**The idea.**
- **Vertical (scale up)**: bigger machine. More RAM, more CPU. Simple, limited by hardware.
- **Horizontal (scale out)**: more machines. Unlimited in theory, but you must handle the *coordination* problem.

**Why it matters.** Most "cloud-native" patterns exist because horizontal scaling is hard, and they make it tractable.

### 🛠️ Activity 5.1: Show why vertical hits a wall (30 min)

Read AWS's EC2 instance types. The biggest one (e.g., `u7in-32tb`) costs ~$50,000/month. Now imagine your app needs 100× that. You've hit the wall — you must scale horizontally.

Write a one-page note answering: *"At what scale does vertical scaling become economically irrational? What problems appear when you go horizontal?"*

---

## 5.2 Stateful vs stateless services

**The idea.** A *stateless* service holds no per-user state in memory between requests. Any instance can serve any request. *Stateful* services (e.g. databases) hold state and must coordinate.

**Why it matters.** Stateless services scale horizontally trivially — just put more instances behind a load balancer. Stateful services are the hard part.

### 🛠️ Activity 5.2: Make a stateful service stateless (60 min)

Build a simple in-memory shopping cart server:

```python
# cart_stateful.py — bad
from flask import Flask, jsonify, request
app = Flask(__name__)
carts = {}  # user_id -> list of items (stored in this process's memory!)

@app.post("/cart/<user>/add")
def add(user):
    carts.setdefault(user, []).append(request.json["item"])
    return jsonify(carts[user])

app.run(port=5000)
```

Run *two* copies on different ports (5000 and 5001). Add an item via 5000. Read via 5001. Different state! This breaks horizontal scaling.

Now refactor to use a shared store (Redis or just SQLite). Both instances read from the same store. Same item is visible from both.

**Done when:** Two instances of the same service share state via an external store and behave identically from the user's perspective.

### 🤔 Reflect

- Where does the "state" actually live now? (In Redis. The service is now stateless.)
- What did we trade for this? (A network hop on every request.)

### ⚠️ Common pitfalls

- "Sticky sessions" (always route the user to the same backend) — works at small scale, breaks during deploys and failures.

---

# Part 6 — The Edge: Reverse Proxies, Load Balancers, CDNs

## 6.1 Reverse proxy

**The idea.** A reverse proxy sits in front of your service(s). Clients talk to it; it forwards to backends. It can do TLS termination, caching, request routing, header rewriting, rate limiting.

**Why it matters.** Almost every production deployment has one. Nginx, Envoy, Caddy, HAProxy, Traefik are common.

### 🛠️ Activity 6.1: Set up Nginx as a reverse proxy (60 min)

Run two copies of your stateless cart service from 5.2 on ports 5000 and 5001. Now run Nginx in Docker:

```nginx
# nginx.conf
events {}
http {
  upstream cart {
    server host.docker.internal:5000;
    server host.docker.internal:5001;
  }
  server {
    listen 80;
    location / {
      proxy_pass http://cart;
    }
  }
}
```

```bash
docker run --rm -p 8080:80 \
    -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
    nginx
```

Now `curl localhost:8080/cart/alice/add ...` and observe Nginx round-robins between your two backends (check each backend's logs).

**Done when:** Repeated requests alternate between backends, and if you stop one backend, requests still succeed (Nginx skips it).

### 🤔 Reflect

- If you didn't have Nginx, where would TLS termination happen? (In your app — far less efficient, more attack surface.)
- What header would tell your backend the *original* client IP? (`X-Forwarded-For`.)

---

## 6.2 Load balancing algorithms

**The idea.** When you have many backends, how do you pick which one handles a request?

- **Round-robin**: rotate through them.
- **Least connections**: pick the one with fewest active connections.
- **Weighted**: bigger machines get more.
- **Power of two choices**: pick two random backends; send to the less-loaded one. Surprisingly close to optimal, no central state.
- **Consistent hashing**: hash the request key (user ID, etc.); minimises rebalancing when backends change.

### 🛠️ Activity 6.2: Build a load balancer in 100 lines (90 min)

```python
# tiny_lb.py
import asyncio, itertools, random
from aiohttp import web, ClientSession, ClientError

BACKENDS = ["http://localhost:5000", "http://localhost:5001"]
algo = "p2c"  # try "rr" or "p2c"

backend_inflight = {b: 0 for b in BACKENDS}
rr_iter = itertools.cycle(BACKENDS)

def pick():
    if algo == "rr":
        return next(rr_iter)
    if algo == "p2c":
        a, b = random.sample(BACKENDS, 2)
        return a if backend_inflight[a] < backend_inflight[b] else b

async def proxy(request):
    backend = pick()
    backend_inflight[backend] += 1
    try:
        async with ClientSession() as s:
            async with s.request(
                request.method, f"{backend}{request.path_qs}",
                data=await request.read(), headers=request.headers
            ) as r:
                body = await r.read()
                return web.Response(body=body, status=r.status, headers=r.headers)
    finally:
        backend_inflight[backend] -= 1

app = web.Application()
app.router.add_route("*", "/{tail:.*}", proxy)
web.run_app(app, port=8080)
```

Make some backends artificially slow (`sleep 1` per request) and stress-test with `wrk` or `hey`. Try `algo = "rr"` and then `algo = "p2c"`. P2C should give you better tail latency.

**Done when:** You see P2C beats round-robin under uneven backend speed.

---

## 6.3 Health checks

**The idea.** A load balancer must not send traffic to dead backends. It periodically pings each (e.g. `GET /healthz`); if no response, removes it from rotation.

### 🛠️ Activity 6.3: Add health checks (45 min)

Extend your tiny_lb:

```python
import time
backend_healthy = {b: True for b in BACKENDS}

async def health_loop():
    while True:
        for b in BACKENDS:
            try:
                async with ClientSession() as s:
                    async with s.get(f"{b}/healthz", timeout=1) as r:
                        backend_healthy[b] = r.status == 200
            except Exception:
                backend_healthy[b] = False
        await asyncio.sleep(2)
```

Pick only from healthy backends. Add a `/healthz` to your cart service. Stop one cart service; observe the LB skips it within 2 seconds.

**Done when:** Killing a backend doesn't cause failed requests after the next health-check cycle.

### 🤔 Reflect

- What's the trade-off in health-check interval? (Faster = quicker recovery; slower = less probe traffic.)
- *Shallow* health check (process is alive) vs. *deep* (DB connection works). Which would you use?

---

## 6.4 CDNs in 5 minutes

**The idea.** A CDN caches static (and increasingly dynamic) content close to the user. The user's request hits the nearest edge. Edge has it → cheap and fast. Edge doesn't → fetches from origin once, caches it.

**Why it matters.** A CDN cuts latency by 10×, cuts your origin bandwidth bill by 10×, and provides DDoS protection. It's free to start with on Cloudflare/Fastly/AWS for small projects.

### 🛠️ Activity 6.4: Put your site on a CDN (45 min, optional cloud)

If you have a domain: put a static page on Cloudflare's free plan. Compare load time from your origin server vs. via Cloudflare. Use `curl -w "%{time_starttransfer}\n"`.

If not: read Cloudflare's "How a request flows through Cloudflare" docs and write a one-page summary.

---

# Part 7 — Caching: The Highest-Leverage Lever

## 7.1 Where you can cache

**The idea.** Caching means storing a computation's result so you don't redo it. You can cache at every level:

1. **Browser** (HTTP cache headers)
2. **CDN** (regional cache)
3. **Reverse proxy** (Nginx, Varnish)
4. **Application memory** (in-process LRU)
5. **Distributed cache** (Redis, Memcached)
6. **Database query cache / materialised views**

The cheaper a cache hit is and the closer it is to the user, the more valuable.

**Why it matters.** Caching is the single highest-impact optimisation in most read-heavy systems.

### 🛠️ Activity 7.1: Profile a slow endpoint and cache it (60 min)

Add a `/expensive` route to your cart service that simulates a slow DB query:

```python
@app.get("/expensive")
def expensive():
    import time; time.sleep(0.5)
    return {"result": 42}
```

Stress it with `hey -n 1000 -c 50 http://localhost:5000/expensive` and note throughput.

Now wrap with a 30-second in-process cache:

```python
from cachetools import TTLCache
cache = TTLCache(maxsize=1000, ttl=30)

@app.get("/expensive")
def expensive():
    if "key" in cache: return cache["key"]
    import time; time.sleep(0.5)
    result = {"result": 42}
    cache["key"] = result
    return result
```

Re-run the stress test. Throughput should jump dramatically.

**Done when:** You measure both versions and can articulate the throughput improvement.

---

## 7.2 LRU cache from scratch

**The idea.** A *Least Recently Used* cache evicts the item that hasn't been touched for the longest. It's the workhorse of in-memory caches.

### 🛠️ Activity 7.2: Implement LRU in 30 lines (60 min)

```python
class LRU:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = {}    # key -> [prev, next, value]
        self.head = ["__head__", None, None, None]
        self.tail = ["__tail__", None, None, None]
        self.head[2] = self.tail
        self.tail[1] = self.head
    
    def _detach(self, node):
        node[1][2] = node[2]
        node[2][1] = node[1]
    
    def _attach_after_head(self, node):
        node[1] = self.head
        node[2] = self.head[2]
        self.head[2][1] = node
        self.head[2] = node
    
    def get(self, key):
        if key not in self.data: return None
        node = self.data[key]
        self._detach(node)
        self._attach_after_head(node)
        return node[3]
    
    def put(self, key, value):
        if key in self.data:
            node = self.data[key]
            node[3] = value
            self._detach(node)
            self._attach_after_head(node)
            return
        if len(self.data) >= self.cap:
            lru_node = self.tail[1]
            self._detach(lru_node)
            del self.data[lru_node[0]]
        node = [key, None, None, value]
        self.data[key] = node
        self._attach_after_head(node)

# Test
lru = LRU(2)
lru.put("a", 1); lru.put("b", 2)
print(lru.get("a"))  # 1; "a" is now most recent
lru.put("c", 3)       # evicts "b"
print(lru.get("b"))  # None
print(lru.get("c"))  # 3
```

**Done when:** Your tests confirm LRU semantics. Compare with Python's `functools.lru_cache` to convince yourself yours behaves the same.

### 🤔 Reflect

- Why does LRU need both a hash map *and* a doubly-linked list? (O(1) lookup AND O(1) reorder.)
- What's a workload where LRU performs *poorly*? (Big sequential scans evict everything useful — see TinyLFU.)

---

## 7.3 Redis: a distributed cache

**The idea.** When you have multiple servers, an in-process cache means each server has its own copy — wasteful and inconsistent. A *shared* cache like Redis lets all servers see the same cache.

### 🛠️ Activity 7.3: Add Redis caching (75 min)

```bash
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

```python
import redis, json, time

r = redis.Redis(decode_responses=True)

def get_user(user_id):
    cache_key = f"user:{user_id}"
    cached = r.get(cache_key)
    if cached:
        return json.loads(cached)
    
    # Simulate slow DB
    time.sleep(0.2)
    user = {"id": user_id, "name": f"User {user_id}"}
    
    r.setex(cache_key, 60, json.dumps(user))  # TTL 60s
    return user

# Test
start = time.perf_counter()
get_user(42)  # cache miss
print(f"Miss: {(time.perf_counter()-start)*1000:.1f} ms")

start = time.perf_counter()
get_user(42)  # cache hit
print(f"Hit: {(time.perf_counter()-start)*1000:.1f} ms")
```

**Done when:** You see hit ≪ miss latency.

---

## 7.4 Cache invalidation — the hard problem

**The idea.** When the underlying data changes, the cache becomes stale. Strategies:

- **TTL (time-to-live)**: cache expires after N seconds. Simple, eventually consistent.
- **Write-through**: writes go to cache *and* DB synchronously.
- **Cache-aside with explicit invalidation**: on write, also delete the cache key.
- **Versioned keys**: include a version in the key (`user:42:v3`); bump version on write.

### 🛠️ Activity 7.4: Show cache staleness, then fix it (60 min)

In your cart service, add a "user profile" route cached in Redis with a 60s TTL. Update the user in the DB directly (via SQLite). Notice the cached version is still served. Now add explicit invalidation: on update, `r.delete(cache_key)`. Verify the next read picks up the new value.

**Done when:** You demonstrate stale-cache, then fix it; you can explain the trade-off of TTL-only vs explicit invalidation.

### ⚠️ Common pitfalls

- **Cache stampede / dogpile**: cache key expires; 1000 concurrent requests miss; all hit the DB. Mitigations: single-flight, probabilistic early expiry, locking-on-miss.
- Caching things that shouldn't be cached (per-user data with a global key — security issue).

---

# Part 8 — Databases at Scale

## 8.1 Replication

**The idea.** Copy data to multiple machines. Why? Survive failure, serve more reads, lower latency by region.

- **Primary-replica (a.k.a. leader-follower)**: one writes, others read. Replicas may lag.
- **Multi-leader**: multiple writers; conflicts must be resolved.
- **Leaderless** (Dynamo-style): writes go to N replicas; reads from N; quorums (W + R > N) ensure consistency.

### 🛠️ Activity 8.1: Set up Postgres replication (90 min)

Use Docker Compose:

```yaml
# docker-compose.yml
services:
  primary:
    image: bitnami/postgresql:16
    environment:
      POSTGRESQL_REPLICATION_MODE: master
      POSTGRESQL_REPLICATION_USER: repl
      POSTGRESQL_REPLICATION_PASSWORD: replpass
      POSTGRESQL_USERNAME: app
      POSTGRESQL_PASSWORD: app
      POSTGRESQL_DATABASE: app
    ports: ["5432:5432"]
  replica:
    image: bitnami/postgresql:16
    environment:
      POSTGRESQL_REPLICATION_MODE: slave
      POSTGRESQL_REPLICATION_USER: repl
      POSTGRESQL_REPLICATION_PASSWORD: replpass
      POSTGRESQL_MASTER_HOST: primary
      POSTGRESQL_PASSWORD: app
    ports: ["5433:5432"]
    depends_on: [primary]
```

`docker-compose up`. Insert into the primary; read from the replica:

```bash
psql postgresql://app:app@localhost:5432/app -c "CREATE TABLE t (id int); INSERT INTO t VALUES (1);"
psql postgresql://app:app@localhost:5433/app -c "SELECT * FROM t;"
```

**Done when:** You can write to primary and read from replica, and you can demonstrate *replication lag* by writing in a tight loop and observing the replica catches up shortly after.

### 🤔 Reflect

- After a write, can a *read on the replica* always see it? (No. There's lag.)
- What if you read your own write? ("Read-your-writes consistency" — often solved by routing the user's reads to primary for a short period after writing.)

---

## 8.2 Sharding (partitioning)

**The idea.** When data outgrows one machine, *split* it across machines. The shard key determines which machine holds each row.

- **Range partitioning**: `user_id 0–1M → shard 1; 1M–2M → shard 2`. Easy range queries; hot-shard risk.
- **Hash partitioning**: `shard = hash(user_id) % N`. Even distribution; range queries become scatter-gather.
- **Consistent hashing**: minimises rebalancing when you add/remove shards.

### 🛠️ Activity 8.2a: Manual sharding (60 min)

Spin up 3 SQLite databases (`shard_0.db`, `shard_1.db`, `shard_2.db`). Build a Python class that hashes the user_id and routes reads/writes to the right shard.

```python
import sqlite3, hashlib

class ShardedKV:
    def __init__(self, num_shards=3):
        self.shards = [
            sqlite3.connect(f"shard_{i}.db") for i in range(num_shards)
        ]
        for s in self.shards:
            s.execute("CREATE TABLE IF NOT EXISTS kv (k TEXT PRIMARY KEY, v TEXT)")
    
    def _shard_for(self, key):
        h = int(hashlib.md5(key.encode()).hexdigest(), 16)
        return self.shards[h % len(self.shards)]
    
    def put(self, k, v):
        s = self._shard_for(k)
        s.execute("INSERT OR REPLACE INTO kv VALUES (?, ?)", (k, v))
        s.commit()
    
    def get(self, k):
        s = self._shard_for(k)
        cur = s.execute("SELECT v FROM kv WHERE k=?", (k,))
        row = cur.fetchone()
        return row[0] if row else None

kv = ShardedKV()
for i in range(100):
    kv.put(f"k{i}", f"value{i}")

# Verify keys are spread across shards
for i, s in enumerate(kv.shards):
    n = s.execute("SELECT COUNT(*) FROM kv").fetchone()[0]
    print(f"shard {i}: {n} keys")
```

**Done when:** You see keys roughly evenly distributed across shards.

### 🛠️ Activity 8.2b: Implement consistent hashing (90 min, stretch)

Try changing `num_shards` from 3 to 4. Most keys get reassigned (because `hash % 3 ≠ hash % 4`). Now implement a consistent hash ring (search "consistent hashing python" for tutorials) and measure: with N→N+1 shards, only ~1/N of keys move.

### 🤔 Reflect

- Sharding makes joins across shards expensive. How would you handle "find me all users with email ending in `@gmail.com`"? (Scatter-gather across all shards.)
- What's the *re-sharding* problem? (Moving data without downtime as the cluster grows.)

---

## 8.3 The classic re-sharding playbook

**The idea.** Memorise this — it's the answer to many "online migration" interview questions.

```
1. Add new shards (capacity weight 0).
2. Dual-write: every write goes to old AND new locations.
3. Backfill historical data into new shards (chunked, throttled).
4. Shadow read: read from both, compare, alert on divergence.
5. Cut reads over to new shards.
6. Stop dual-writing; decommission old.
```

### 🛠️ Activity 8.3: Write a one-page migration plan (45 min)

Imagine your `ShardedKV` from above is in production with 3 shards and you need to grow to 4. Write a step-by-step plan following the pattern above. Include:

- How long each step takes.
- How you'd measure success.
- How you'd roll back at each step.

Save it. Re-read it before any interview.

---

# Part 9 — Distributed Systems: Why It's Hard

## 9.1 The eight fallacies

**The idea.** Peter Deutsch's eight fallacies of distributed computing — every one is false in production:

1. The network is reliable.
2. Latency is zero.
3. Bandwidth is infinite.
4. The network is secure.
5. Topology doesn't change.
6. There is one administrator.
7. Transport cost is zero.
8. The network is homogeneous.

**Why it matters.** Every "weird bug" comes from forgetting one of these.

### 🛠️ Activity 9.1: Simulate a network partition (75 min)

Use Docker Compose with two services and a `tc`-based network simulator (or just kill the network):

```bash
docker-compose up -d
# Now break the network from one container
docker exec primary tc qdisc add dev eth0 root netem loss 100%
# ...wait, observe
docker exec primary tc qdisc del dev eth0 root
```

Or simpler: use `iptables -A INPUT -s <other_ip> -j DROP` to one-way-block. Watch your replication lag explode and your client get errors.

**Done when:** You've observed a real network partition and noted what your client / replica did. (Hint: they hung. They didn't get a clean error.)

---

## 9.2 CAP, in plain English

**The idea.** When the network partitions, you must choose:

- **CP** (Consistency + Partition tolerance): refuse to serve writes (or reads) on the wrong side of the partition. Linearizable, but unavailable. Examples: ZooKeeper, etcd, traditional RDBMS clusters.
- **AP** (Availability + Partition tolerance): keep serving on both sides; reconcile later. Eventually consistent. Examples: DynamoDB, Cassandra (tunable).

You **cannot** have all three. You can choose where on the spectrum to be.

**PACELC** extends this: even when there's no partition, you choose between Latency and Consistency.

### 🛠️ Activity 9.2: Choose CP or AP for these scenarios (60 min)

Write your choice for each, with a one-sentence justification:

1. A bank's account balance.
2. Twitter's like counter.
3. An e-commerce inventory.
4. A real-time multiplayer game's leaderboard.
5. WhatsApp message delivery.
6. A DNS server.
7. A flight booking system (last seat!).
8. A "users you may know" recommendation.
9. A configuration store for microservices.
10. A distributed log of user clicks.

Compare with peers or look up real systems' choices.

**Done when:** You can defend each choice and acknowledge cases where it's actually fine to be eventually consistent.

---

## 9.3 Time and clocks

**The idea.** There is no global clock in a distributed system. Wall clocks drift; NTP can jump backwards. You need *logical* clocks that capture *causality*.

- **Lamport timestamps**: a monotonic counter per process. On send, include the counter; on receive, set local = max(local, received) + 1. Gives a total order consistent with causality.
- **Vector clocks**: one counter per process. Detects concurrency (events with neither happens-before).

### 🛠️ Activity 9.3: Implement Lamport timestamps (60 min)

Simulate three processes that exchange messages:

```python
class Process:
    def __init__(self, name):
        self.name = name
        self.clock = 0
    
    def local_event(self):
        self.clock += 1
        print(f"{self.name}: local event @ {self.clock}")
    
    def send(self, other):
        self.clock += 1
        msg = (f"hi from {self.name}", self.clock)
        print(f"{self.name}: send @ {self.clock}")
        other.receive(msg)
    
    def receive(self, msg):
        text, ts = msg
        self.clock = max(self.clock, ts) + 1
        print(f"{self.name}: receive '{text}' @ {self.clock}")

a, b, c = Process("A"), Process("B"), Process("C")
a.local_event()
a.send(b)
b.local_event()
b.send(c)
c.local_event()
c.send(a)
```

**Done when:** You can manually trace through and see why Lamport timestamps preserve cause-before-effect.

### 🤔 Reflect

- Two events have Lamport timestamps 5 and 7. Did event 5 *cause* event 7? (Maybe; we can't tell from Lamport alone — need vector clocks.)
- Why can wall clocks not be used as Lamport clocks? (Drift, NTP jumps, no causal monotonicity.)

---

# Part 10 — Consensus and Coordination

## 10.1 Why consensus matters

**The idea.** Many distributed systems need agreement on a single value: who's the leader, what's the next log entry, what's the current config. *Consensus* algorithms (Paxos, Raft) make N machines agree even if some fail.

**Why it matters.** Almost every distributed database, queue, and orchestrator (etcd, Kafka, ZooKeeper, CockroachDB) uses consensus internally.

### 🛠️ Activity 10.1: Run etcd, watch a leader election (60 min)

```bash
docker run -d --name etcd-1 -p 2379:2379 -p 2380:2380 \
    quay.io/coreos/etcd:v3.5.0 \
    etcd --name node1 --initial-advertise-peer-urls http://localhost:2380 \
    --listen-peer-urls http://0.0.0.0:2380 \
    --listen-client-urls http://0.0.0.0:2379 \
    --advertise-client-urls http://localhost:2379
```

Run a 3-node etcd cluster (search "etcd docker-compose 3 nodes"). Watch logs to see leader election. Stop the leader; watch a new one elected.

**Done when:** You've observed a leader change in real time, and you understand etcd survives 1 of 3 nodes failing but not 2.

### 🤔 Reflect

- Why is the *quorum* (majority) needed for consensus? (Prevents split-brain.)
- A 3-node cluster tolerates 1 failure; a 5-node cluster tolerates 2. So why doesn't everyone run 99-node clusters? (Each consensus round needs a majority of acks → larger cluster = slower writes.)

---

## 10.2 Distributed locks (with fencing tokens)

**The idea.** Coordinate work across processes by acquiring a lock from a central service. Naive locks have a serious bug: the lock holder pauses (GC, network), the lease expires, someone else takes the lock, and then the original wakes up still believing it has the lock. *Fencing tokens* (monotonically increasing IDs from the lock service) prevent this.

### 🛠️ Activity 10.2: Build a Redis lock with fencing (90 min)

```python
import redis, time

r = redis.Redis(decode_responses=True)

def acquire(name, ttl=10):
    # Use SET with NX (only-if-not-exists) and EX (expiry)
    token = r.incr(f"fence:{name}")  # monotonically increasing
    ok = r.set(f"lock:{name}", str(token), nx=True, ex=ttl)
    return token if ok else None

def release(name, token):
    # Lua script for atomic "if matches, delete"
    script = """
    if redis.call("get", KEYS[1]) == ARGV[1] then
        return redis.call("del", KEYS[1])
    else
        return 0
    end
    """
    return r.eval(script, 1, f"lock:{name}", str(token))

def critical_work_with_token(name, token, storage):
    # Storage system MUST check fence token before applying writes
    last_token = int(storage.get("last_token") or 0)
    if token < last_token:
        raise Exception("Stale lock!")
    storage["last_token"] = token
    print(f"Did work with token {token}")

# Try it
storage = {}
token = acquire("widget")
print(f"Got lock with token {token}")
critical_work_with_token("widget", token, storage)
release("widget", token)
```

**Done when:** You can simulate a "GC pause": acquire a lock, sleep 12s (past the 10s TTL), have another process acquire it (gets a higher token), then your old process tries to write — and it's rejected because of the lower fence token.

### ⚠️ Common pitfalls

- Using a lock without fencing — the bug exists, you just haven't seen it yet.
- Forgetting to release on error paths — set TTL so locks self-release.

---

# Part 11 — Messaging: Queues, Logs, Streams

## 11.1 Why async messaging

**The idea.** Synchronous calls (A calls B, waits for response) couple A's availability to B's. Asynchronous messaging (A puts a message in a queue, B reads when ready) decouples them.

**Why it matters.** Almost every real backend has at least one queue or log. They handle bursts (buffering), retries (durability), and architectural decoupling.

### 🛠️ Activity 11.1: Run RabbitMQ and Kafka (60 min)

```bash
# RabbitMQ — classic queue
docker run -d --name rabbit -p 5672:5672 -p 15672:15672 rabbitmq:3-management

# Kafka — distributed log
docker run -d --name kafka -p 9092:9092 \
    -e KAFKA_CFG_NODE_ID=0 \
    -e KAFKA_CFG_PROCESS_ROLES=controller,broker \
    -e KAFKA_CFG_LISTENERS=PLAINTEXT://:9092,CONTROLLER://:9093 \
    -e KAFKA_CFG_LISTENER_SECURITY_PROTOCOL_MAP=CONTROLLER:PLAINTEXT,PLAINTEXT:PLAINTEXT \
    -e KAFKA_CFG_ADVERTISED_LISTENERS=PLAINTEXT://localhost:9092 \
    -e KAFKA_CFG_CONTROLLER_QUORUM_VOTERS=0@localhost:9093 \
    -e KAFKA_CFG_CONTROLLER_LISTENER_NAMES=CONTROLLER \
    bitnami/kafka:latest
```

Visit `http://localhost:15672` (RabbitMQ admin, guest/guest) to see the queue UI.

---

## 11.2 Queue vs log

**The idea.**
- **Queue** (RabbitMQ, SQS): a message is *consumed once*, then deleted. New consumer doesn't see history. Good for job dispatch.
- **Log** (Kafka, Kinesis, Pulsar): a message is *retained* for a period. Each consumer reads from its own offset. Multiple independent consumers; new consumer can replay history.

**Why it matters.** Logs decouple producers from consumers in *time* and in *count*. Almost every modern data architecture relies on this property.

### 🛠️ Activity 11.2: Build the same producer-consumer twice (90 min)

**RabbitMQ version:**

```python
# producer.py
import pika
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
ch = conn.channel()
ch.queue_declare(queue="orders", durable=True)
for i in range(10):
    ch.basic_publish("", "orders", f"order-{i}",
        properties=pika.BasicProperties(delivery_mode=2))
conn.close()

# consumer.py
import pika
conn = pika.BlockingConnection(pika.ConnectionParameters("localhost"))
ch = conn.channel()
ch.queue_declare(queue="orders", durable=True)
def cb(ch, method, props, body):
    print(f"got {body.decode()}")
    ch.basic_ack(method.delivery_tag)
ch.basic_consume("orders", cb)
ch.start_consuming()
```

Run producer; run consumer; ack and consume the messages. Now start a *second* consumer — it gets nothing because the first already ate the messages.

**Kafka version:**

```python
# producer.py
from kafka import KafkaProducer
p = KafkaProducer(bootstrap_servers="localhost:9092")
for i in range(10):
    p.send("orders", f"order-{i}".encode())
p.flush()

# consumer.py
from kafka import KafkaConsumer
c = KafkaConsumer("orders",
    bootstrap_servers="localhost:9092",
    group_id="my-group",
    auto_offset_reset="earliest")
for msg in c:
    print(f"got {msg.value.decode()}")
```

Run producer. Run consumer with `group_id="g1"`. Now run *another* consumer with `group_id="g2"` — it sees the *same messages*, because each group has its own offset.

**Done when:** You can articulate when you'd reach for a queue vs a log.

---

## 11.3 Delivery semantics and idempotency

**The idea.**
- *At-most-once*: fast, may lose messages. Rare in practice.
- *At-least-once*: retried until acked; may duplicate. **The default.** Make consumers idempotent.
- *Exactly-once*: requires cooperation (Kafka transactions). Often achieved at the application layer with idempotency keys.

**Idempotent consumer:** processing the same message twice has the same result as once.

### 🛠️ Activity 11.3: Build an idempotent consumer (60 min)

Have your Kafka consumer maintain a *processed message ID* set in Redis (or SQLite). Each message has a UUID. Before processing, check if the UUID has been seen; if so, skip.

```python
import redis
r = redis.Redis(decode_responses=True)

def process_idempotent(msg_id, payload):
    # SET only if not exists; returns True if newly set
    if r.set(f"processed:{msg_id}", "1", nx=True, ex=86400):
        # First time seeing this message
        do_work(payload)
    else:
        print(f"Skipping duplicate {msg_id}")
```

Test by injecting a duplicate. Verify do_work runs once.

**Done when:** Duplicates are silently dropped without breaking correctness.

### ⚠️ Common pitfalls

- Believing "Kafka exactly-once" magically works — it requires careful producer + consumer + sink configuration.
- Idempotency keys with too-short TTL — duplicates that arrive late re-process.

---

## 11.4 Backpressure

**The idea.** When consumers can't keep up with producers, you need a strategy. Bounded queues are a form of backpressure (producers block). Pull-based consumers (Kafka) are inherently backpressured: the consumer pulls only what it can handle.

### 🛠️ Activity 11.4: Demonstrate consumer lag in Kafka (45 min)

Start a slow consumer (e.g. `time.sleep(1)` per message). Pump 1000 messages quickly. Use Kafka's `kafka-consumer-groups.sh --describe --group my-group --bootstrap-server localhost:9092` to see *consumer lag* (how many messages behind).

**Done when:** You see lag grow, plateau, then drain. Discuss: at what lag would you alert? At what lag would you scale up consumers?

---

# Part 12 — Data Pipelines: Batch and Stream

## 12.1 Batch ETL pipeline

**The idea.** Periodically (hourly, daily) take raw data, transform it, and load it into a destination optimised for queries.

### 🛠️ Activity 12.1: Build a daily ETL (90 min)

Generate fake events into Postgres `events_raw`:

```python
# load_raw.py
import psycopg2, random, datetime
con = psycopg2.connect("dbname=app user=app password=app host=localhost")
cur = con.cursor()
cur.execute("CREATE TABLE IF NOT EXISTS events_raw (ts TIMESTAMPTZ, user_id INT, event TEXT, value FLOAT)")
for _ in range(100000):
    cur.execute("INSERT INTO events_raw VALUES (%s, %s, %s, %s)",
        (datetime.datetime.now() - datetime.timedelta(seconds=random.randint(0, 86400)),
         random.randint(1, 1000), random.choice(["click", "view", "purchase"]),
         random.uniform(0, 100)))
con.commit()
```

Now write an ETL job that aggregates: hourly counts per event_type per user.

```python
# etl.py
cur.execute("""
CREATE TABLE IF NOT EXISTS events_hourly (
    hour TIMESTAMPTZ, user_id INT, event TEXT, count INT, total_value FLOAT,
    PRIMARY KEY (hour, user_id, event)
)
""")
cur.execute("""
INSERT INTO events_hourly (hour, user_id, event, count, total_value)
SELECT date_trunc('hour', ts), user_id, event, COUNT(*), SUM(value)
FROM events_raw
WHERE ts >= NOW() - INTERVAL '1 day'
GROUP BY 1, 2, 3
ON CONFLICT (hour, user_id, event)
DO UPDATE SET count = EXCLUDED.count, total_value = EXCLUDED.total_value
""")
con.commit()
```

**Done when:** You can rerun the ETL idempotently (the `ON CONFLICT` clause handles re-runs).

### 🤔 Reflect

- Idempotency is critical for ETL: you must be able to rerun without duplicating. How would you do this if your destination didn't support `UPSERT`?
- What's the trade-off between processing the last hour every minute vs the last day every hour?

---

## 12.2 Streaming basics

**The idea.** Process events as they arrive, in small windows, with low latency. Tools: Kafka Streams, Flink, Spark Structured Streaming, Faust.

### 🛠️ Activity 12.2: Build a tumbling-window stream processor (90 min)

Without a framework — just to internalise the concepts:

```python
# stream_processor.py
from kafka import KafkaConsumer
from collections import defaultdict
from datetime import datetime, timedelta
import json

c = KafkaConsumer("events", bootstrap_servers="localhost:9092",
                  value_deserializer=lambda b: json.loads(b))

window_size = timedelta(seconds=10)
windows = defaultdict(lambda: defaultdict(int))  # window_start -> event_type -> count

for msg in c:
    event = msg.value
    event_time = datetime.fromisoformat(event["ts"])
    window_start = event_time.replace(microsecond=0)
    window_start = window_start - timedelta(
        seconds=window_start.second % 10
    )
    windows[window_start][event["event_type"]] += 1
    
    # Periodically emit and prune old windows
    cutoff = datetime.utcnow() - timedelta(minutes=1)
    for w in list(windows.keys()):
        if w < cutoff:
            print(f"WINDOW {w}: {dict(windows[w])}")
            del windows[w]
```

Have your producer emit events with `ts` and `event_type` fields. Watch windowed aggregates print every 10 seconds.

**Done when:** You see the per-window counts, and you can articulate the difference between *event time* (when the event happened) and *processing time* (when you saw it).

### 🤔 Reflect

- What if an event arrives 1 minute late? Does it land in the right window? (With this code, no — you've already evicted that window.)
- What if you want a *sliding* window (last 10 seconds, every 1 second) instead? (Different windowing logic.)

---

## 12.3 CDC (Change Data Capture)

**The idea.** Stream a database's changes (inserts/updates/deletes) into downstream systems in near-real-time. Powers cache invalidation, search index updates, OLTP→OLAP replication, microservice decoupling.

### 🛠️ Activity 12.3: CDC with Postgres + Debezium (120 min, stretch)

Set up Debezium to read Postgres's WAL and publish row changes to Kafka:

1. Configure Postgres for logical replication.
2. Run Debezium connector pointing at Postgres → Kafka.
3. Insert a row in Postgres. Watch a JSON event appear in a Kafka topic.

**Done when:** You see real DB changes flowing as Kafka events.

If this is too much setup, just *read* the Debezium tutorial and write a one-page summary of how log-based CDC works.

---

# Part 13 — ML Systems: From Notebook to Production

## 13.1 The ML system lifecycle

**The idea.** Training a model is the easy part. Productionising it requires:

```
Data → Validation → Features → Training → Eval → Registry → Deploy → 
Serve → Monitor → Retrain
```

Every arrow has failure modes. ML platform engineering is making each arrow reliable.

### 🛠️ Activity 13.1: Train your first deployable model (90 min)

```python
# train.py
import sklearn.datasets, sklearn.linear_model, joblib

X, y = sklearn.datasets.load_iris(return_X_y=True)
model = sklearn.linear_model.LogisticRegression(max_iter=200).fit(X, y)
joblib.dump(model, "model.pkl")
print(f"Train accuracy: {model.score(X, y):.3f}")
```

Now serve it:

```python
# serve.py
from fastapi import FastAPI
from pydantic import BaseModel
import joblib, numpy as np

app = FastAPI()
model = joblib.load("model.pkl")

class Input(BaseModel):
    features: list[float]

@app.post("/predict")
def predict(inp: Input):
    arr = np.array(inp.features).reshape(1, -1)
    pred = model.predict(arr)[0]
    proba = model.predict_proba(arr)[0]
    return {"prediction": int(pred), "probabilities": proba.tolist()}

# Run: uvicorn serve:app --port 8000
```

`curl -X POST localhost:8000/predict -H 'Content-Type: application/json' -d '{"features":[5.1,3.5,1.4,0.2]}'`

**Done when:** You have a model file + an HTTP API that serves predictions.

---

## 13.2 Experiment tracking

**The idea.** Without tracking, you can't reproduce experiments, compare models, or know what's in production. MLflow / Weights & Biases / Comet handle this.

### 🛠️ Activity 13.2: Track experiments with MLflow (75 min)

```bash
pip install mlflow
mlflow server --host 0.0.0.0 --port 5000   # or just `mlflow ui`
```

```python
import mlflow, sklearn.datasets, sklearn.ensemble

mlflow.set_tracking_uri("http://localhost:5000")
mlflow.set_experiment("iris")

X, y = sklearn.datasets.load_iris(return_X_y=True)

for n in [10, 50, 200]:
    with mlflow.start_run():
        mlflow.log_param("n_estimators", n)
        m = sklearn.ensemble.RandomForestClassifier(n_estimators=n).fit(X, y)
        score = m.score(X, y)
        mlflow.log_metric("accuracy", score)
        mlflow.sklearn.log_model(m, "model")
```

Visit `localhost:5000`, see all three runs, compare them.

**Done when:** You can compare runs in the UI and understand why this beats "I ran it locally and forgot the params."

---

## 13.3 Feature engineering and feature stores

**The idea.** Features are the *inputs* to the model. The same feature must be computed identically at training time (offline, on historical data) and serving time (online, on live data). Mismatch = "training-serving skew" — a top cause of model degradation.

A *feature store* is a data system that stores features once, serves them both offline and online, and guarantees consistency.

### 🛠️ Activity 13.3: Build a tiny feature store (120 min)

Build a system where features are computed once and used by both batch training and online serving.

```python
# feature_store.py
import redis, sqlite3, json, time

r = redis.Redis(decode_responses=True)
db = sqlite3.connect("features.db")
db.execute("""
CREATE TABLE IF NOT EXISTS user_features (
    user_id INT, ts TIMESTAMP,
    n_purchases_30d INT, total_spend_30d REAL,
    PRIMARY KEY (user_id, ts)
)""")

def materialise(user_id):
    """Compute features and store in BOTH offline (sqlite) and online (redis)."""
    # Pretend this comes from your event warehouse:
    n_purchases = 5  # SELECT COUNT(*) FROM events WHERE user_id=? AND ts > NOW() - 30d
    total_spend = 234.56
    
    now = int(time.time())
    db.execute("INSERT OR REPLACE INTO user_features VALUES (?, ?, ?, ?)",
               (user_id, now, n_purchases, total_spend))
    db.commit()
    
    # Online store - fast key-value lookup
    r.hset(f"features:user:{user_id}", mapping={
        "n_purchases_30d": n_purchases,
        "total_spend_30d": total_spend,
        "ts": now
    })

def get_online(user_id):
    """Fast lookup for serving."""
    return r.hgetall(f"features:user:{user_id}")

def get_offline(user_id, as_of_ts):
    """Point-in-time correct lookup for training."""
    cur = db.execute("""
        SELECT * FROM user_features 
        WHERE user_id = ? AND ts <= ? 
        ORDER BY ts DESC LIMIT 1
    """, (user_id, as_of_ts))
    return cur.fetchone()
```

**Done when:** You can articulate (a) why we use Redis for serving and SQLite for training, (b) what *point-in-time correctness* means, (c) how this prevents training-serving skew.

### 🤔 Reflect

- Why is "join your training labels with current feature values" a bug? (Label leakage — your features at training time saw the future.)
- What is *point-in-time-correct join*? (Each training row gets the features as they were *at the prediction time*, not as they are now.)

---

## 13.4 Model registry and deployment

**The idea.** A model registry stores model artifacts + metadata + lineage + stage (staging / production). Deploying a model means promoting an entry in the registry; rollback means reverting.

### 🛠️ Activity 13.4: Promote and roll back a model (60 min)

Using the MLflow setup from 13.2:

1. Pick your best run, register the model: `mlflow.register_model(...)` — name it `iris_classifier`.
2. Promote it to stage `Staging`.
3. Train a new (slightly different) model; register version 2; stage it.
4. Promote v2 to `Production`. Roll v1 back to `Archived`.
5. Modify your `serve.py` to load `models:/iris_classifier/Production`.
6. Now demote v2 and promote v1 — observe `serve.py` picks up v1 on restart.

**Done when:** You've done a deploy and a rollback through the registry, no code changes.

---

## 13.5 Online model monitoring

**The idea.** A deployed model can degrade silently:
- **Operational drift**: latency increases, errors grow.
- **Data drift**: input distributions shift (new app version sends different data).
- **Concept drift**: the world changes; old patterns don't predict.

You monitor all three.

### 🛠️ Activity 13.5: Add drift detection (75 min)

Maintain rolling histograms of feature values. Compare today's distribution to a baseline using Population Stability Index (PSI):

```python
import numpy as np

def psi(expected, actual, bins=10):
    edges = np.linspace(min(expected.min(), actual.min()),
                        max(expected.max(), actual.max()), bins+1)
    e, _ = np.histogram(expected, bins=edges)
    a, _ = np.histogram(actual, bins=edges)
    e = e / e.sum() + 1e-6
    a = a / a.sum() + 1e-6
    return np.sum((a - e) * np.log(a / e))

# baseline (from training):
baseline = np.random.normal(50, 10, 1000)
# today (synthetic shift):
today = np.random.normal(55, 12, 1000)

print(f"PSI: {psi(baseline, today):.3f}")
# < 0.1 = no drift; 0.1-0.25 = moderate; > 0.25 = significant
```

**Done when:** You can flag a synthetic shift and articulate at what threshold you'd retrain.

---

# Part 14 — ML at Scale: GPUs and Distributed Training

## 14.1 GPU basics, just enough to be dangerous

**The idea.** A GPU has thousands of cores optimised for parallel arithmetic on big arrays (matrix math). It has its own memory (HBM) which is fast but limited (40–80 GB on H100). The bottleneck is usually *memory bandwidth*, not compute.

**Why it matters.** Training and serving big models requires GPU. Knowing what they're good at (huge parallel batch math) and bad at (random branching, small ops) shapes every design decision.

### 🛠️ Activity 14.1: Train a model on a free GPU (90 min)

Open Google Colab; switch runtime to GPU (T4 is free).

```python
import torch
print(torch.cuda.is_available(), torch.cuda.get_device_name(0))

import time
n = 5000
a = torch.randn(n, n)
b = torch.randn(n, n)

# CPU
start = time.perf_counter()
c = a @ b
print(f"CPU matmul: {time.perf_counter()-start:.2f}s")

# GPU
a, b = a.cuda(), b.cuda()
torch.cuda.synchronize()
start = time.perf_counter()
c = a @ b
torch.cuda.synchronize()
print(f"GPU matmul: {time.perf_counter()-start:.2f}s")
```

You'll see the GPU is dramatically faster.

Now train MNIST. Use a simple CNN; train for 1 epoch on CPU and on GPU. Compare wall-clock time.

**Done when:** You've seen 10–100× speedup on a real workload, and you understand *why* (parallel matrix math).

---

## 14.2 Mixed precision and memory

**The idea.** Default neural net training uses FP32 (4 bytes/number). FP16 / BF16 (2 bytes) doubles your effective memory and speeds up math on tensor cores. Tiny accuracy cost; massive throughput win.

### 🛠️ Activity 14.2: Compare FP32 vs BF16 training (75 min)

```python
import torch.cuda.amp as amp

# Original loop
for X, y in loader:
    optimizer.zero_grad()
    out = model(X)
    loss = loss_fn(out, y)
    loss.backward()
    optimizer.step()

# Mixed-precision loop
scaler = amp.GradScaler()
for X, y in loader:
    optimizer.zero_grad()
    with amp.autocast(dtype=torch.bfloat16):
        out = model(X)
        loss = loss_fn(out, y)
    scaler.scale(loss).backward()
    scaler.step(optimizer)
    scaler.update()
```

Time both. Note GPU memory usage (`torch.cuda.max_memory_allocated()`).

**Done when:** You see speedup *and* lower memory usage; you can explain why.

---

## 14.3 Distributed training: data parallelism

**The idea.** Split the *batch* across N GPUs. Each GPU has a full model copy, processes its slice, computes gradients. Then *all-reduce* the gradients across GPUs (everyone ends with the sum). Apply the update; everyone is in sync.

### 🛠️ Activity 14.3: Run PyTorch DDP locally (120 min)

If you have one GPU, you can simulate with two processes on the same device:

```python
# train_ddp.py
import os, torch, torch.distributed as dist
import torch.nn as nn
from torch.nn.parallel import DistributedDataParallel as DDP

def main(rank, world):
    os.environ["MASTER_ADDR"] = "localhost"
    os.environ["MASTER_PORT"] = "29500"
    dist.init_process_group("nccl" if torch.cuda.is_available() else "gloo",
                            rank=rank, world_size=world)
    
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = nn.Linear(100, 10).to(device)
    ddp_model = DDP(model, device_ids=[rank] if device.type == "cuda" else None)
    
    optimizer = torch.optim.Adam(ddp_model.parameters(), lr=1e-3)
    for step in range(20):
        x = torch.randn(32, 100).to(device)
        y = torch.randint(0, 10, (32,)).to(device)
        out = ddp_model(x)
        loss = nn.functional.cross_entropy(out, y)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        if rank == 0:
            print(f"step {step}: loss {loss.item():.4f}")
    
    dist.destroy_process_group()

if __name__ == "__main__":
    import torch.multiprocessing as mp
    world = 2
    mp.spawn(main, args=(world,), nprocs=world)
```

Run it. Observe both processes train; loss decreases.

**Done when:** You've run DDP and can articulate (a) what `all_reduce` does, (b) when DDP scales sub-linearly (communication overhead), (c) the difference between data parallelism and model parallelism.

---

## 14.4 Other parallelisms (read + diagram)

**The idea.** When the model itself doesn't fit on one GPU, you also need:

- **Tensor parallelism (TP)**: split individual layers across GPUs. Megatron-LM.
- **Pipeline parallelism (PP)**: place different layers on different GPUs; mini-batches flow through stages.
- **FSDP / ZeRO**: shard *optimizer state, gradients, and parameters* across data-parallel workers; recovers most of DP's simplicity at much lower memory.
- **Sequence/Context parallelism**: shard the sequence dimension; needed for long-context training.

For LLMs, you typically *combine* these: TP within a node (NVLink fast), PP across nodes, DP/FSDP across pipeline groups.

### 🛠️ Activity 14.4: Draw the picture (60 min)

On paper or any drawing tool, draw a 64-GPU cluster (8 nodes × 8 GPUs/node) training a 70B parameter model with:

- TP=8 (one tensor-parallel group per node).
- PP=4 (4 pipeline stages across nodes).
- DP=2 (2 data-parallel replicas).

Verify: 8 × 4 × 2 = 64 ✓. Mark which GPU does what for one minibatch flowing through.

**Done when:** Your diagram is correct and you can talk through it for two minutes.

---

## 14.5 Fine-tune a small LLM (the centrepiece)

**The idea.** Pretraining a frontier LLM costs $10M+. *Fine-tuning* a small open-weights model on your data costs <$10. The technique: LoRA (Low-Rank Adaptation) — freeze the base weights; train tiny adapter matrices.

### 🛠️ Activity 14.5: LoRA fine-tune in Colab (180 min)

In Colab with a T4 GPU:

```python
!pip install transformers peft datasets bitsandbytes accelerate trl

from transformers import AutoTokenizer, AutoModelForCausalLM
from peft import LoraConfig, get_peft_model, TaskType
from trl import SFTTrainer, SFTConfig
from datasets import load_dataset

model_name = "Qwen/Qwen2.5-0.5B"  # tiny, fits on free Colab
tok = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

lora = LoraConfig(
    task_type=TaskType.CAUSAL_LM,
    r=8, lora_alpha=16, lora_dropout=0.05,
    target_modules=["q_proj", "v_proj"]
)
model = get_peft_model(model, lora)
model.print_trainable_parameters()
# Should print something like: trainable: ~1M / total: ~500M

# Tiny dataset for demo
ds = load_dataset("databricks/databricks-dolly-15k", split="train[:500]")
def fmt(x):
    return {"text": f"### Instruction:\n{x['instruction']}\n\n### Response:\n{x['response']}"}
ds = ds.map(fmt)

trainer = SFTTrainer(
    model=model,
    train_dataset=ds,
    args=SFTConfig(output_dir="./out", num_train_epochs=1, 
                    per_device_train_batch_size=4,
                    gradient_accumulation_steps=4, learning_rate=2e-4,
                    bf16=True, logging_steps=10),
)
trainer.train()
trainer.save_model("./out")
```

Then:

```python
# Inference
prompt = "### Instruction:\nWrite a haiku about distributed systems.\n\n### Response:\n"
inputs = tok(prompt, return_tensors="pt").to(model.device)
out = model.generate(**inputs, max_new_tokens=100)
print(tok.decode(out[0]))
```

**Done when:** Your fine-tuned model produces noticeably different outputs than the base model on the kind of instructions you trained on. You understand: what LoRA freezes, what it trains, why it's so much cheaper.

### 🤔 Reflect

- Why does LoRA work? (Most of the model's "language understanding" is in pretrained weights; we need tiny adjustments for new tasks.)
- What's the trade-off vs full fine-tuning? (Less expressive; usually fine for narrow tasks.)

---

# Part 15 — LLM Systems: RAG, Fine-Tuning, Serving

## 15.1 Tokenisation and the cost of inference

**The idea.** LLMs operate on *tokens* (sub-word units). A typical English sentence is ~75% as many tokens as words. Cost and latency scale with tokens.

### 🛠️ Activity 15.1: Explore tokenisation (45 min)

```python
from transformers import AutoTokenizer

for model_name in ["gpt2", "Qwen/Qwen2.5-0.5B", "meta-llama/Llama-3.2-1B"]:
    try:
        tok = AutoTokenizer.from_pretrained(model_name)
        text = "Distributed systems are hard."
        ids = tok.encode(text)
        print(f"{model_name}: {len(ids)} tokens: {[tok.decode([t]) for t in ids]}")
    except Exception as e:
        print(f"{model_name}: skipping ({e})")
```

Try with: code (lots of tokens), Hindi/Devanagari text (often *very* expensive in older tokenisers), JSON.

**Done when:** You see different tokenisers produce different token counts for the same text, and you understand cost implications for non-English / structured data.

---

## 15.2 Vector embeddings

**The idea.** An embedding turns text (or anything) into a fixed-size vector such that semantically similar things have similar vectors. The basis of semantic search.

### 🛠️ Activity 15.2: Build embeddings, see similarity (60 min)

```python
from sentence_transformers import SentenceTransformer
import numpy as np

m = SentenceTransformer("all-MiniLM-L6-v2")

texts = [
    "I love distributed systems",
    "Distributed systems are fascinating",
    "I'd like a pizza please",
    "What's a good pizza topping?",
    "How does Kafka work?",
]

emb = m.encode(texts, normalize_embeddings=True)
print(f"Shape: {emb.shape}")  # (5, 384)

# Similarity = dot product (since normalised)
sim = emb @ emb.T
print(np.round(sim, 2))
```

You'll see similar pairs have high similarity (~0.7+) and unrelated pairs are near 0.

**Done when:** You see "love distributed systems" is similar to "distributed systems are fascinating" but *not* to "pizza please."

---

## 15.3 Vector databases

**The idea.** Store millions/billions of vectors; given a query vector, find the K most similar fast. Done via Approximate Nearest Neighbour (ANN) algorithms — HNSW, IVF, PQ. Trade a tiny recall loss for huge speedup.

### 🛠️ Activity 15.3: Use pgvector (90 min)

```bash
docker run -d --name pgv -p 5432:5432 \
    -e POSTGRES_PASSWORD=pass pgvector/pgvector:pg16
```

```python
import psycopg2, numpy as np
from sentence_transformers import SentenceTransformer

con = psycopg2.connect("dbname=postgres user=postgres password=pass host=localhost")
cur = con.cursor()
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
cur.execute("DROP TABLE IF EXISTS docs")
cur.execute("CREATE TABLE docs (id serial PRIMARY KEY, text text, emb vector(384))")

m = SentenceTransformer("all-MiniLM-L6-v2")

corpus = [
    "Kafka is a distributed log",
    "Postgres is a relational database",
    "Redis is an in-memory key-value store",
    "Cassandra is a wide-column NoSQL database",
    "Spark processes large datasets",
    "Pizza is a delicious Italian dish",
    "Pasta carbonara uses eggs and bacon",
]
embs = m.encode(corpus, normalize_embeddings=True)
for text, emb in zip(corpus, embs):
    cur.execute("INSERT INTO docs (text, emb) VALUES (%s, %s)",
                (text, emb.tolist()))
con.commit()

# Query
q = m.encode(["What's a good distributed messaging system?"], 
             normalize_embeddings=True)[0].tolist()
cur.execute("SELECT text, 1 - (emb <=> %s::vector) as sim FROM docs ORDER BY emb <=> %s::vector LIMIT 3",
            (q, q))
for row in cur.fetchall():
    print(row)
```

**Done when:** Your top-3 results are the relevant ones (Kafka, Cassandra, others) and the pizza ones are filtered out.

### 🛠️ Activity 15.3b: Scale up with an HNSW index (60 min, stretch)

Generate 100K random vectors (or use a real dataset like Wikipedia abstracts). Time queries with and without `CREATE INDEX ... USING hnsw`. You should see 100×+ speedup.

---

## 15.4 Build a RAG system

**The idea.** Retrieval-Augmented Generation: instead of relying solely on the LLM's parametric knowledge, retrieve relevant context from a knowledge base and put it in the prompt.

```
User query
  → embed
  → vector search → top-K docs
  → put docs in prompt
  → LLM generates response with citations
```

### 🛠️ Activity 15.4: End-to-end RAG over your own docs (180 min)

Pick a small corpus: your notes, a few PDFs, your company's docs.

1. **Ingest**: split into chunks of ~500 tokens; embed; store in pgvector.
2. **Retrieve**: given a question, embed it, find top-K chunks.
3. **Generate**: stuff retrieved chunks into a prompt; call an LLM; return answer + citations.

```python
def rag(question):
    # 1. Embed the question
    q_emb = embedder.encode([question], normalize_embeddings=True)[0]
    
    # 2. Retrieve top-K
    cur.execute("""
        SELECT text FROM docs 
        ORDER BY emb <=> %s::vector LIMIT 5
    """, (q_emb.tolist(),))
    chunks = [r[0] for r in cur.fetchall()]
    
    # 3. Build prompt
    context = "\n---\n".join(chunks)
    prompt = f"""Answer based on the context. If the context doesn't help, say so.

Context:
{context}

Question: {question}

Answer:"""
    
    # 4. Call LLM (use your fine-tuned model from 14.5, or a hosted API)
    response = llm.generate(prompt)
    return response, chunks  # answer + citations
```

**Done when:** You can ask questions over your own corpus and the system pulls the relevant chunks. Try a question whose answer is *not* in the corpus — does it hallucinate or correctly say "I don't know"?

### 🤔 Reflect

- What if a chunk is too big? Too small?
- What if the query is "compare X and Y" but X and Y are in *different* chunks? (Hint: query rewriting; fetch more chunks.)
- How do you evaluate a RAG system? (Recall@K of retrieval; faithfulness of generated answer; citation accuracy.)

### ⚠️ Common pitfalls

- Naive fixed-size chunking that splits in the middle of a sentence.
- Forgetting to normalise embeddings → distance metric is wrong.
- Hallucinations — the model answers despite irrelevant context. Mitigate with stricter prompts, refusal training, citation requirements.

---

## 15.5 Serve an LLM efficiently

**The idea.** LLM inference has two phases:

- **Prefill**: process the prompt; compute-bound.
- **Decode**: generate one token at a time; *memory-bandwidth-bound* (each new token reads the full KV cache + weights).

Optimisations: continuous batching (vLLM), PagedAttention, quantisation (FP8, INT4), KV-cache reuse for shared prefixes.

### 🛠️ Activity 15.5: Serve with vLLM (90 min, GPU required)

```bash
pip install vllm
python -m vllm.entrypoints.openai.api_server \
    --model Qwen/Qwen2.5-0.5B \
    --port 8000
```

It exposes an OpenAI-compatible API. Hit it:

```python
import openai
client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="dummy")
r = client.chat.completions.create(
    model="Qwen/Qwen2.5-0.5B",
    messages=[{"role": "user", "content": "Hello"}]
)
print(r.choices[0].message.content)
```

Now load-test with 10 concurrent clients. vLLM's continuous batching should give you near-linear throughput scaling.

**Done when:** You measure tokens-per-second under load and can articulate why batching at the *token level* (vLLM's core trick) beats batching whole requests.

---

# Part 16 — Observability

## 16.1 Metrics, logs, traces

**The idea.** The three pillars of observability:

- **Metrics**: numeric time series. "request rate", "p99 latency", "queue depth". Cheap to store; aggregate.
- **Logs**: structured (JSON, please) text events. "User 42 logged in".
- **Traces**: end-to-end span trees of a single request crossing multiple services.

### 🛠️ Activity 16.1: Add Prometheus metrics (75 min)

```bash
pip install prometheus-client
```

```python
from prometheus_client import Counter, Histogram, start_http_server
import time, random

REQUESTS = Counter('http_requests_total', 'Total requests', ['endpoint', 'status'])
LATENCY = Histogram('http_latency_seconds', 'Latency', ['endpoint'])

def handle_request(endpoint):
    with LATENCY.labels(endpoint=endpoint).time():
        time.sleep(random.uniform(0, 0.5))
        status = random.choice(["200", "200", "200", "500"])
        REQUESTS.labels(endpoint=endpoint, status=status).inc()

start_http_server(9100)
while True:
    handle_request(random.choice(["/api/users", "/api/orders"]))
    time.sleep(0.1)
```

Visit `http://localhost:9100/metrics` — you'll see Prometheus-format text. Run Prometheus in Docker pointed at your scrape target; install Grafana; build a dashboard with rate, p50, p95, p99 by endpoint.

**Done when:** You have a Grafana dashboard with at least 4 panels, and you can spot the simulated 500s.

---

## 16.2 Structured logging

**The idea.** Logs as JSON > logs as prose. Searchable, parseable, machine-friendly.

### 🛠️ Activity 16.2: Add structured logging (45 min)

```python
import structlog, logging

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)
log = structlog.get_logger()

log.info("request_received", endpoint="/api/users", user_id=42, latency_ms=123)
```

Output: `{"endpoint": "/api/users", "user_id": 42, ..., "event": "request_received"}`.

**Done when:** Every log line in your service is JSON with consistent fields (timestamp, level, request_id, etc.).

---

## 16.3 Distributed tracing

**The idea.** When a request hops across 5 services, you want to see *where* the time went. Distributed tracing assigns a `trace_id` at the entry point and propagates it; each service emits *spans* with timing.

### 🛠️ Activity 16.3: Add OpenTelemetry tracing (90 min)

```bash
pip install opentelemetry-api opentelemetry-sdk \
    opentelemetry-exporter-otlp-proto-grpc \
    opentelemetry-instrumentation-fastapi
```

Run Jaeger locally:
```bash
docker run -d --name jaeger -p 16686:16686 -p 4317:4317 \
    jaegertracing/all-in-one:latest
```

In your FastAPI service:

```python
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

trace.set_tracer_provider(TracerProvider())
trace.get_tracer_provider().add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="localhost:4317", insecure=True))
)
FastAPIInstrumentor().instrument_app(app)
```

Make a few requests. Visit `http://localhost:16686` (Jaeger UI). See trace waterfalls.

**Done when:** You can see one request's span tree and identify which sub-call took the longest.

---

## 16.4 SLOs and error budgets

**The idea.** An *SLO* (Service Level Objective) is a target ("99.9% of requests succeed within 200 ms over 30 days"). The *error budget* is `1 - SLO` (0.1% — i.e., ~43 minutes/month of badness). Spend it on shipping features. When exhausted, freeze and stabilise.

### 🛠️ Activity 16.4: Define SLOs for your service (45 min)

For your cart service from earlier, write:

1. Two SLIs (e.g., "successful request ratio", "p95 latency").
2. Two SLOs (e.g., "99.5% successful over 30 days", "p95 < 200 ms").
3. The corresponding error budgets.
4. What you'd do when they're exhausted.

**Done when:** You have a one-page SLO doc that engineering, product, and SRE could agree on.

---

# Part 17 — Reliability: Designing for Failure

## 17.1 Retries with exponential backoff and jitter

**The idea.** Transient failures (network hiccup, DB blip) are expected. Retry — but carefully. Naive retries cause *thundering herds* (everyone retrying together) which prolong outages. Add exponential backoff (1s, 2s, 4s, 8s) and *jitter* (randomise) to spread out retries.

### 🛠️ Activity 17.1: Implement retry with backoff + jitter (45 min)

```python
import time, random
from functools import wraps

def retry_with_backoff(max_attempts=5, base=1.0, cap=30.0):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return fn(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise
                    sleep = min(cap, base * (2 ** attempt)) * (0.5 + random.random())
                    print(f"Attempt {attempt+1} failed: {e}; sleeping {sleep:.2f}s")
                    time.sleep(sleep)
        return wrapper
    return decorator

@retry_with_backoff(max_attempts=4)
def flaky():
    if random.random() < 0.7:
        raise Exception("transient failure")
    return "success"

print(flaky())
```

**Done when:** You see retries with growing-but-jittered delays, eventually succeeding.

### ⚠️ Common pitfalls

- Retrying non-idempotent operations (e.g., charging a credit card). Always pair retries with idempotency keys.
- Not capping retries — you can wait forever.

---

## 17.2 Circuit breakers

**The idea.** A circuit breaker tracks downstream health. When too many calls fail, it *opens* (immediately rejects without calling), giving the downstream time to recover. Periodically tries again (half-open). Prevents cascading failures.

### 🛠️ Activity 17.2: Build a circuit breaker (75 min)

```python
import time, random
from enum import Enum

class State(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"

class CircuitBreaker:
    def __init__(self, fail_threshold=5, reset_after=10):
        self.state = State.CLOSED
        self.failures = 0
        self.fail_threshold = fail_threshold
        self.reset_after = reset_after
        self.opened_at = 0
    
    def call(self, fn, *args, **kwargs):
        if self.state == State.OPEN:
            if time.time() - self.opened_at > self.reset_after:
                self.state = State.HALF_OPEN
                print("→ HALF_OPEN")
            else:
                raise Exception("Circuit open!")
        
        try:
            result = fn(*args, **kwargs)
            if self.state == State.HALF_OPEN:
                self.state = State.CLOSED
                self.failures = 0
                print("→ CLOSED")
            return result
        except Exception as e:
            self.failures += 1
            if self.failures >= self.fail_threshold:
                self.state = State.OPEN
                self.opened_at = time.time()
                print("→ OPEN")
            raise

cb = CircuitBreaker()
def flaky():
    if random.random() < 0.9:
        raise Exception("downstream error")
    return "ok"

for i in range(30):
    try:
        result = cb.call(flaky)
        print(f"{i}: {result}")
    except Exception as e:
        print(f"{i}: {e}")
    time.sleep(0.5)
```

Watch the breaker open after enough failures, refuse fast for a while, then half-open and try again.

**Done when:** You can articulate the three states and what triggers transitions.

---

## 17.3 Chaos engineering

**The idea.** *Inject* failures in production (or staging) to verify your system tolerates them. Netflix's Chaos Monkey randomly kills VMs. The point: discover bugs *before* they hit you in the middle of the night.

### 🛠️ Activity 17.3: Chaos test your stack (90 min)

In Docker Compose, you have your service + Postgres + Redis + Kafka. Run a load test (~100 req/s for 5 minutes). During the test, do each of these one at a time:

1. `docker pause redis` for 10 seconds, then unpause.
2. `docker stop postgres-replica` (the read replica).
3. Add 200 ms latency to the network: `docker exec service tc qdisc add dev eth0 root netem delay 200ms`.
4. Kill one of two service instances.

For each: observe what happens. Record: did requests fail? Did latency spike? Did the system recover automatically?

**Done when:** You have a one-page chaos report with what you learned and at least two actionable improvements.

---

# Part 18 — Security Basics

## 18.1 Authentication

**The idea.** *Authentication* (authn) is "who are you?" *Authorization* (authz) is "what can you do?" Standards: OAuth2 (delegation), OIDC (identity on top of OAuth2), JWT (compact tokens).

### 🛠️ Activity 18.1: Add JWT auth to your API (90 min)

```python
import jwt, time
from fastapi import FastAPI, HTTPException, Depends, Header

SECRET = "dev-secret-do-not-use-in-prod"
app = FastAPI()

@app.post("/login")
def login(username: str, password: str):
    # In real life: check DB; hash passwords with bcrypt/argon2; rate-limit.
    if username == "alice" and password == "wonderland":
        token = jwt.encode(
            {"sub": username, "exp": int(time.time()) + 3600},
            SECRET, algorithm="HS256"
        )
        return {"token": token}
    raise HTTPException(401)

def auth(authorization: str = Header(...)):
    try:
        token = authorization.removeprefix("Bearer ").strip()
        return jwt.decode(token, SECRET, algorithms=["HS256"])
    except Exception:
        raise HTTPException(401)

@app.get("/me")
def me(claims=Depends(auth)):
    return {"user": claims["sub"]}
```

**Done when:** You can log in, get a token, hit `/me` with the token, and have it rejected without one or with an expired one.

### 🤔 Reflect

- Why are JWTs *signed*, not encrypted? (Anyone can read them; only the server can mint them.)
- What happens if your secret leaks? (Anyone can mint tokens. Rotate secrets and use short TTLs.)
- Why short TTLs? (Limit blast radius if a token is stolen.)

---

## 18.2 TLS, secrets, and the basics

**The idea.**
- **TLS everywhere**: in transit, even between services in the same VPC. mTLS (mutual TLS) for service-to-service.
- **Encryption at rest**: storage layer should encrypt with KMS-managed keys.
- **Secrets**: never in code or in git. Use Vault / AWS Secrets Manager / Kubernetes Secrets / sealed secrets.
- **Least privilege**: every service has the minimum permissions it needs, no more.

### 🛠️ Activity 18.2: Audit your local stack for secrets (30 min)

Search your project: `grep -rn "password\|secret\|api_key" .`

Fix anything in code/config to use environment variables loaded from a `.env` file (which is *gitignored*).

**Done when:** No secrets in source; `.env.example` is checked in; the real `.env` is not.

---

# Part 19 — Capstone Project: Document Intelligence Platform

This capstone integrates everything from Parts 1–18 into a single production-grade system. Build it over 4–6 weeks. By the end, you can speak to every system design topic *from experience*.

## 19.1 The product

A multi-tenant **Document Intelligence Platform**:

- Users upload PDFs and other documents.
- The platform indexes them for hybrid (keyword + vector) search.
- Users chat with their corpus via a RAG-powered LLM endpoint.
- Admins can fine-tune a small base LLM on tenant-specific data.
- Everything is observable, auth'd, rate-limited, and cost-attributed per tenant.

## 19.2 Architecture overview

```
                  ┌──────────────┐
            ────► │ API Gateway  │ (auth, rate limit, routing)
                  └──────┬───────┘
                         │
       ┌─────────────────┼──────────────────┐
       ▼                 ▼                  ▼
┌─────────────┐  ┌──────────────┐  ┌────────────────┐
│ Upload Svc  │  │  Search Svc  │  │   Chat Svc     │
│  (FastAPI)  │  │  (FastAPI)   │  │   (FastAPI)    │
└──────┬──────┘  └──────┬───────┘  └────────┬───────┘
       │                │                   │
       ▼                ▼                   ▼
┌─────────────────────────────────────────────────────┐
│                 Kafka (event bus)                    │
└─────────────────────────────────────────────────────┘
       │                                    │
       ▼                                    ▼
┌──────────────┐                  ┌────────────────────┐
│ Index Worker │                  │ Embedding Worker   │
│ (extract,    │                  │ (chunk → embed)    │
│  parse, OCR) │                  │                    │
└──────┬───────┘                  └─────────┬──────────┘
       │                                    │
       ▼                                    ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ Postgres     │  │ MinIO (S3)   │  │ pgvector     │  │ Redis        │
│ (metadata)   │  │ (originals)  │  │ (embeddings) │  │ (cache,      │
│              │  │              │  │              │  │  features)   │
└──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘
       
                  ┌──────────────────────────┐
                  │ vLLM (LLM serving)        │
                  │ + LoRA fine-tuned model   │
                  └──────────────────────────┘

                  ┌──────────────────────────┐
                  │ Prometheus + Grafana      │
                  │ Loki (logs)               │
                  │ Jaeger (traces)           │
                  └──────────────────────────┘
```

## 19.3 Milestones

### Milestone 1 — Skeleton (week 1)

**Build:**
- FastAPI service with `POST /documents` (upload) and `GET /documents/{id}` endpoints.
- Postgres for metadata; MinIO (Docker) for object storage.
- JWT auth with two roles: `user`, `admin`.
- Tenant isolation: every row carries `tenant_id`.

**Wires up Parts:** 1, 2, 3, 5, 18.

**Done when:** A user from tenant A cannot see tenant B's documents, even by guessing IDs.

### Milestone 2 — Async processing pipeline (week 1–2)

**Build:**
- On upload, write to Postgres + emit Kafka event using the **outbox pattern** (atomic).
- Index Worker consumes the event: extracts text from PDF, splits into chunks, persists chunks to Postgres.
- Bounded queue + circuit breaker around the parser (some PDFs are giant or malformed).

**Wires up Parts:** 4, 11, 17.

**Done when:** You can upload 100 PDFs in parallel; they all index without OOM; one malformed PDF doesn't poison the queue.

### Milestone 3 — Search service (week 2)

**Build:**
- Embedding Worker consumes "chunk indexed" events; embeds with sentence-transformers; writes to pgvector.
- `POST /search` does **hybrid search**: BM25 (Postgres full-text) + vector ANN; fuse with reciprocal rank fusion.
- Cache search results in Redis (cache-aside, 60s TTL, explicit invalidation on document re-index).

**Wires up Parts:** 7, 15.

**Done when:** Searches return relevant results in <100 ms p95.

### Milestone 4 — Chat service with RAG (week 3)

**Build:**
- vLLM serving a small base model (e.g. Qwen 2.5 3B).
- `POST /chat` endpoint: retrieves top-K chunks → builds prompt with citations → streams response.
- Per-tenant token budget: token-bucket rate limiter using Redis.
- Per-request cost accounting (tokens consumed, by tenant).

**Wires up Parts:** 14, 15.

**Done when:** A user can ask questions over their documents and get cited answers; rate-limit kicks in correctly; cost per tenant is visible in Grafana.

### Milestone 5 — Fine-tuning pipeline (week 4) ⭐

**Build:**
- Admin endpoint `POST /finetune` triggers a LoRA fine-tune job on the tenant's documents (synthetic Q&A → SFT).
- Use Colab or a rented GPU VM for the actual training.
- Track in MLflow; register the model.
- Deploy: vLLM loads the LoRA adapter on demand for that tenant; chat requests for that tenant use it.

**Wires up Parts:** 13, 14.

**Done when:** A fine-tuned model produces measurably better answers for the tenant who trained it.

### Milestone 6 — Observability & SLOs (week 5)

**Build:**
- Prometheus scraping every service.
- Grafana dashboards: per-service RED metrics, per-tenant cost, retrieval recall.
- Loki for logs; Jaeger for traces.
- Define SLOs for each public endpoint; alert when error budget burns >2× target.

**Wires up Parts:** 16.

**Done when:** Open Grafana → in 30 seconds, you can answer: which tenant is using the most tokens? Which endpoint is slowest? Are we burning error budget?

### Milestone 7 — Reliability (week 5–6)

**Build:**
- Chaos test: kill workers, partition Redis, throttle Kafka.
- Verify graceful degradation (search falls back to BM25-only when vector search is unhealthy).
- Canary deploys via blue-green or feature flags.
- Backup/restore drill: simulate Postgres loss, restore from backup, verify integrity.

**Wires up Parts:** 17.

**Done when:** You've run a chaos game day, written a postmortem, and shipped at least two improvements.

### Milestone 8 — Final polish

**Build:**
- A simple frontend (Streamlit is fine — this isn't a frontend course).
- A README with the architecture diagram, key trade-offs, and "what I'd do with more time."
- A 15-minute video walkthrough of the system.

**Done when:** Someone could clone your repo, follow the README, and have it running in 30 minutes.

## 19.4 What you can say in interviews after this

> *"In a project I built, I had to handle backpressure when the embedding worker fell behind. I used a bounded Kafka consumer with a Prometheus metric on consumer lag, and when lag exceeded 10K I horizontally scaled workers. The bottleneck turned out to be the embedding model itself; I switched to batch embedding with a 32-item batch and got 4× throughput. Trade-off was an extra 200 ms of p95 latency on the *first* document in a batch, but average latency improved."*

That sentence pattern, applied to caching, retries, distributed locks, fine-tuning, etc., is what gets you Staff offers.

---

# Part 20 — Interview Frameworks and Communication

## 20.1 The RESHADED framework

A reusable scaffold. Use this for *every* system design question.

| Phase | What you do | Time (45-min interview) |
|---|---|---|
| **R**equirements | Functional + non-functional + constraints + assumptions | 5–8 min |
| **E**stimation | QPS, storage, bandwidth, memory, cost | 3–5 min |
| **S**chema / data model | Entities, relationships, access patterns | 3–5 min |
| **H**igh-level design | API + components + dataflow | 8–10 min |
| **A**PI design | Concrete endpoints, payloads, semantics | 3–5 min |
| **D**eep dives | The 2–3 hard parts the interviewer cares about | 10–15 min |
| **E**dge cases & failure modes | What breaks, how you detect, how you recover | 3–5 min |
| **D**eployment & operations | Observability, rollout, capacity, on-call | 2–3 min |

### 🛠️ Activity 20.1: Apply RESHADED in 45 minutes (60 min total: 45 design + 15 review)

Pick: "Design a URL shortener." Set a 45-minute timer. Walk through every phase, *out loud*, on paper or whiteboard. After, watch yourself: where did you spend too much time? Where did you skip?

**Done when:** You can mechanically walk through all 8 phases without forgetting any.

---

## 20.2 The first ten minutes are 50% of your score

**Memorise this opening sequence:**

1. **Restate the problem.** Two sentences. Confirms understanding.
2. **Functional requirements.** 4–6 bullets. Defer the rest explicitly.
3. **Non-functional requirements.** Numbers, not adjectives. (DAU, QPS, p99, availability, consistency.)
4. **Out of scope.** Two or three things. Senior signal.
5. **Estimation.** QPS, storage/year, peak bandwidth. Show arithmetic.

Only **then** draw boxes.

### 🛠️ Activity 20.2: Drill the opening (45 min)

Pick three problems (URL shortener, Twitter, Uber). Time yourself doing *just* the opening for each: 10 minutes max. Record audio. Listen back. Trim filler words.

**Done when:** Each opening is crisp, fits in 8–10 minutes, and ends with five quantified estimates.

---

## 20.3 Communication norms that score points

- **Think out loud.** The interviewer grades your *process*, not your final whiteboard.
- **Ask before assuming, then state your assumption.** "Are users globally distributed? I'll assume yes, with majority in NA/EU."
- **Quantify always.** "Hot" → "top 0.1% of keys carry 30% of reads."
- **Disagree gracefully.** When pushed back on something correct, restate the trade-off and let the interviewer decide. Don't collapse; don't dig in.
- **End on trade-offs.** "Given more time, I'd dig into X, because Y."

## 20.4 Anti-patterns that lose points

- Jumping to architecture before requirements.
- Over-engineering for fictional scale ("we'll need Spanner with TrueTime" for a 1 KQPS internal tool).
- Magic boxes labelled "ML" or "AI" with no internals.
- Ignoring failure, monitoring, deployment.
- Inability to defend a storage choice.
- Hand-waving on consistency.
- No discussion of cost.

---

# Part 21 — Mock Interview Bank with Self-Grading Rubric

## 21.1 How to use this bank

Pick a question. Set a 45-minute timer. Walk through using RESHADED, *out loud*, into a recording. Then self-grade with the rubric in §21.4. Fix the lowest-scoring dimension. Repeat with a new question.

Do at least **20 mocks** before your real interview. The first 5 will be bad; you'll see steady improvement.

## 21.2 Easy / warm-up (target: Senior, ~30 min each)

1. Design a URL shortener (bit.ly).
2. Design Pastebin.
3. Design a rate limiter as a service.
4. Design an API gateway.
5. Design a logging service for a fleet of microservices.
6. Design a notification system (email + push + SMS).
7. Design a leaderboard for a game.
8. Design a distributed cache.
9. Design a webhook delivery service (with retries and ordering).
10. Design a key-value store with replication.
11. Design a TinyURL with custom aliases.
12. Design a typeahead/autocomplete service.

## 21.3 Hard / data and ML focus (target: Staff/Principal, ~45 min each)

1. Design Twitter's home timeline (push vs pull vs hybrid; celebrity problem).
2. Design YouTube (upload, transcode, watch path, recommendations).
3. Design Uber's matching service (geo-indexing, surge pricing, ETA).
4. Design Netflix's content delivery (Open Connect, ABR, pre-positioning).
5. Design a real-time fraud detection system at 100K TPS.
6. Design a recommendation system for an e-commerce site (cold start, exploration, business rules).
7. Design a feature store from scratch.
8. Design a real-time bidding (RTB) system for ads (10ms p99, 1M QPS).
9. Design a search system over a billion documents.
10. Design Slack (channels, presence, search, threading, multi-device sync).
11. Design a multi-tenant data warehouse query engine.
12. Design a time-series database.
13. Design a CDC pipeline from MySQL to BigQuery with <1 minute lag.
14. Design a Kafka-like distributed log from scratch.
15. Design Stripe's payments API (idempotency, exactly-once, webhooks).
16. Design Dropbox's sync engine (chunking, dedup, conflict resolution).
17. Design Google Docs (collaborative editing, OT vs CRDT, presence).
18. Design Spotify's music recommendation.
19. Design an LLM serving platform.
20. Design a vector database at billion scale.
21. Design "people you may know" at billion scale.
22. Design an A/B testing platform (assignment, metrics, significance, guardrails).
23. Design a distributed training scheduler for GPU clusters.
24. Design a model marketplace (thousands of customer-uploaded models).
25. Design an agentic system that can browse the web and complete multi-step tasks.
26. Design a global content moderation pipeline (image + text + video).
27. Design a duplicate-content detection system at internet scale.
28. Design a metrics & observability platform (Prometheus-scale).
29. Design a code-search engine over a 100M-file monorepo.
30. Design a system that trains and serves a *personalised* model per user.

## 21.4 Self-assessment rubric

Score each dimension 1–5; total /40.

| Dimension | 1 (Junior) | 3 (Senior) | 5 (Staff/Principal) |
|---|---|---|---|
| **Requirements clarification** | Jumps to design | Lists FRs and NFRs | Quantifies, scopes out, identifies hidden requirements |
| **Estimation** | Skips it | Computes QPS / storage | Drives design from numbers; revisits when assumptions change |
| **High-level design** | Vague boxes | Standard architecture | Customised to constraints; defends each component |
| **Data model** | Glosses over | Reasonable schema | Picks storage from access patterns; addresses evolution |
| **Deep dive** | Surface-level | One thoughtful drill-down | Two-three drills with quantitative trade-offs |
| **Failure modes** | Ignored | Names a few | Systematic blast-radius reasoning, detection, recovery |
| **Operations** | Ignored | Mentions metrics & deploys | SLOs, observability, deploy strategy, on-call |
| **Communication** | Monologues or stalls | Clear, structured | Drives the conversation; invites pushback; defends gracefully |

**Targets:** Senior ≥24. Staff ≥32. Principal ≥36 *and* original insight on at least one trade-off.

## 21.5 Running mocks with a peer (or with an LLM)

**With a peer:** they read the prompt; you design out loud; they push back at least 3 times during deep-dives; afterwards spend 15 minutes on rubric feedback.

**With an LLM (Claude, GPT, etc.):**
- Paste this entire course as context.
- Ask: "Act as an interviewer. Pick a question from Part 21.3. Push back when I oversimplify. After 45 minutes, score me with the rubric."
- Voice mode is even better — you must speak it, not type it.

**With yourself (when no one is around):** record audio. The gap between what you *thought* you said and what you actually said is where 80% of improvement happens.

---

# Appendix A — Numbers to Memorise

**Latency hierarchy:**
- L1 cache: ~1 ns
- L2 cache: ~4 ns
- Main memory: ~100 ns
- SSD random read (NVMe): ~10 µs
- Datacenter RTT: ~500 µs
- Cross-region RTT: ~50–150 ms
- HDD seek: ~10 ms

**Throughput / capacity:**
- Modern CPU core: ~1–10 GFLOPS scalar, much more with SIMD
- One H100 GPU: ~989 TFLOPS (FP16 with sparsity)
- One NVMe drive: ~3–7 GB/s sequential, ~500K–1M IOPS
- 10 GbE NIC: ~1.25 GB/s; 100 GbE: ~12.5 GB/s
- One commodity server: tens of thousands of QPS for simple HTTP, low thousands for DB writes

**Time:**
- 1 day ≈ 86,400 s; round to 100,000 in interviews
- 100K QPS sustained = ~8.6B requests/day
- 1 year ≈ 31.5M s

**Storage rules of thumb:**
- 1 KB per typical user record
- 100 bytes per typical event/log line
- A tweet ≈ 280 chars ≈ 280–1000 B with metadata
- High-res photo: ~1–5 MB; minute of 1080p video: ~50–100 MB

**Cloud unit economics (rough):**
- Object storage: ~$0.02/GB-month
- Block SSD: ~$0.10/GB-month
- Egress to internet: ~$0.05–0.09/GB
- Spot A100: ~$1–2/hour; on-demand H100: ~$3–10/hour
- vCPU-hour: ~$0.04

**Availability:**
- 99% = 3.65 days downtime/year
- 99.9% = 8.76 hours/year
- 99.99% = 52.56 min/year
- 99.999% = 5.26 min/year

---

# Appendix B — Reading List

**Books — distributed systems and data (read in this order):**
1. *Designing Data-Intensive Applications* — Martin Kleppmann. *The* book for this curriculum.
2. *Database Internals* — Alex Petrov.
3. *Site Reliability Engineering* (Google).
4. *Release It!* — Michael Nygard.

**Books — ML systems:**
5. *Designing Machine Learning Systems* — Chip Huyen.
6. *Machine Learning Engineering* — Andriy Burkov.

**Papers — durable classics:**
- The Google File System; MapReduce; Bigtable; Dynamo; Spanner.
- The Tail at Scale.
- Dapper (distributed tracing).
- Kafka: a Distributed Messaging System for Log Processing.
- Attention Is All You Need.
- Megatron-LM, ZeRO, FlashAttention, vLLM (PagedAttention).

**Engineering blogs (highest signal):**
Netflix, Uber, Meta, Stripe, Discord, Figma, Cloudflare, Anthropic, Pinterest, Airbnb, LinkedIn, DoorDash. Read deep-dives, not announcements.

**Individual blogs:**
- Marc Brooker (AWS principal engineer) — distributed systems intuition.
- Brendan Gregg — performance.

---

# Appendix C — A 14-Week Study Plan

Designed for ~10 hours/week. Compress for full-time study.

| Week | Focus | Deliverables |
|---|---|---|
| 1 | Parts 1–2 | All activities done; "first 10 minutes" drilled on 3 problems |
| 2 | Part 3 | KV store + SQLite work complete |
| 3 | Part 4 | Concurrent server + producer-consumer + deadlock demo |
| 4 | Parts 5–6 | Stateless cart service + Nginx LB + tiny LB built |
| 5 | Part 7 | LRU built; Redis cache integrated; cache invalidation demo |
| 6 | Part 8 | Postgres replication + sharding work; re-sharding plan written |
| 7 | Parts 9–10 | Lamport clocks; etcd cluster; distributed lock with fencing |
| 8 | Parts 11–12 | Kafka pipeline + idempotent consumer + tumbling-window processor |
| 9 | Part 13 | Train→serve→track flow; tiny feature store |
| 10 | Part 14 | DDP locally; LoRA fine-tune in Colab |
| 11 | Part 15 | RAG end-to-end; vLLM serving |
| 12 | Parts 16–18 | Observability stack; chaos test; auth |
| 13 | Capstone (Part 19) milestones 1–4 | Document Intelligence MVP |
| 14 | Capstone milestones 5–8 + mocks | Fine-tune deployed; 8+ mock interviews completed |

---

# Final Word

You will be tempted to skip activities and "just read." Don't. The course works because you build. After three months of doing the work, you will not be reciting answers in the interview — you will be remembering the time you debugged a deadlock, watched a leader election, profiled a slow endpoint, and shipped a fine-tuned model.

That is what gets the offer.

Now start with Activity 1.1.
