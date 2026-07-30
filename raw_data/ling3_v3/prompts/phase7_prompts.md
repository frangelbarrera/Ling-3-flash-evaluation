# Phase 7 — Code Review Prompts

## 7.1 Security Bug Detection (20 snippets)

### idor_1_python (Python) — Expected: ['IDOR (CWE-639)', 'SQLi (CWE-89)']
```
@app.route('/user/<user_id>')
def get_user(user_id):
    q = "SELECT * FROM users WHERE id = " + user_id
    cur = db.execute(q)
    user = cur.fetchone()
    return jsonify(user)

```

### idor_2_node (Node.js) — Expected: ['IDOR (CWE-639)']
```
app.get('/api/orders/:id', (req, res) => {
  const order = await Order.findById(req.params.id);
  res.json(order);
});

```

### idor_3_rails (Ruby/Rails) — Expected: ['IDOR (CWE-639)']
```
def show
  @document = Document.find(params[:id])
  render json: @document
end

```

### idor_4_django (Python/Django) — Expected: ['IDOR (CWE-639)']
```
def get_profile(request, user_id):
    profile = Profile.objects.get(pk=user_id)
    return JsonResponse(model_to_dict(profile))

```

### idor_5_go (Go) — Expected: ['IDOR (CWE-639)']
```
func getUser(w http.ResponseWriter, r *http.Request) {
    userID := r.URL.Query().Get("id")
    var user User
    db.Where("id = ?", userID).First(&user)
    json.NewEncoder(w).Encode(user)
}

```

### sqli_1_python (Python) — Expected: ['SQLi (CWE-89)']
```
def search(name):
    query = f"SELECT * FROM products WHERE name LIKE '%{name}%'"
    return db.execute(query).fetchall()

```

### sqli_2_php (PHP) — Expected: ['SQLi (CWE-89)']
```
<?php
$id = $_GET['id'];
$sql = "SELECT * FROM products WHERE id = " . $id;
$result = mysqli_query($conn, $sql);
?>

```

### sqli_3_java (Java) — Expected: ['SQLi (CWE-89)']
```
@GetMapping("/users")
public List<User> search(@RequestParam String name) {
    String sql = "SELECT * FROM users WHERE name = '" + name + "'";
    return jdbcTemplate.queryForList(sql, User.class);
}

```

### sqli_4_csharp (C#) — Expected: ['SQLi (CWE-89)']
```
public User GetUser(string id) {
    string sql = $"SELECT * FROM Users WHERE UserId = {id}";
    return db.Query<User>(sql).FirstOrDefault();
}

```

### sqli_5_ruby (Ruby) — Expected: ['SQLi (CWE-89)']
```
def lookup
    query = "SELECT * FROM items WHERE name = '#{params[:name]}'"
    results = ActiveRecord::Base.connection.execute(query)
    render json: results
end

```

### xss_1_python (Python/Flask) — Expected: ['XSS (CWE-79)']
```
@app.route('/greet')
def greet():
    name = request.args.get('name')
    return f"<h1>Hello, {name}!</h1>"

```

### xss_2_php (PHP) — Expected: ['XSS (CWE-79)']
```
<?php
echo "<div>Welcome, " . $_GET['user'] . "!</div>";
?>

```

### xss_3_node (Node.js) — Expected: ['XSS (CWE-79)']
```
app.get('/profile', (req, res) => {
  const name = req.query.name;
  res.send(`<h1>Welcome ${name}</h1>`);
});

```

### xss_4_react (React/JSX) — Expected: ['XSS (CWE-79)']
```
function Comment({ user }) {
  return <div dangerouslySetInnerHTML={{ __html: user.bio }} />;
}

```

### xss_5_django (Python/Django) — Expected: ['XSS (CWE-79)']
```
def view_post(request, post_id):
    post = Post.objects.get(pk=post_id)
    return HttpResponse(f"<h2>{post.title}</h2><p>{post.content}</p>")

```

### ssrf_1_python (Python) — Expected: ['SSRF (CWE-918)']
```
@app.route('/fetch')
def fetch_url():
    url = request.args.get('url')
    response = requests.get(url)
    return response.text

```

### ssrf_2_node (Node.js) — Expected: ['SSRF (CWE-918)']
```
app.get('/proxy', async (req, res) => {
  const target = req.query.url;
  const response = await fetch(target);
  const text = await response.text();
  res.send(text);
});

```

### ssrf_3_php (PHP) — Expected: ['SSRF (CWE-918)']
```
<?php
$url = $_GET['url'];
echo file_get_contents($url);
?>

```

### ssrf_4_go (Go) — Expected: ['SSRF (CWE-918)']
```
func proxy(w http.ResponseWriter, r *http.Request) {
    target := r.URL.Query().Get("url")
    resp, _ := http.Get(target)
    body, _ := ioutil.ReadAll(resp.Body)
    w.Write(body)
}

```

### ssrf_5_rails (Ruby/Rails) — Expected: ['SSRF (CWE-918)']
```
def fetch
    require 'open-uri'
    url = params[:url]
    content = URI.open(url).read
    render plain: content
end

```


## 7.2 SAFE Snippets (10) — should report NO bugs

### safe_1_python (Python)
```
@app.route('/user/<int:user_id>')
@login_required
def get_user(user_id):
    if user_id != current_user.id and not current_user.is_admin:
        abort(403)
    user = User.query.get(user_id)
    return jsonify(user.to_dict())

```

### safe_2_node (Node.js)
```
app.get('/api/orders/:id', auth, async (req, res) => {
  if (req.params.id !== req.user.id && !req.user.isAdmin) return res.status(403).end();
  const order = await Order.findById(req.params.id);
  if (!order || order.userId !== req.user.id) return res.status(404).end();
  res.json(order);
});

```

### safe_3_django (Python/Django)
```
def get_profile(request, user_id):
    if request.user.id != user_id and not request.user.is_staff:
        raise PermissionDenied()
    profile = Profile.objects.get(pk=user_id)
    return JsonResponse(model_to_dict(profile))

```

### safe_4_sqli (Python)
```
def search(name):
    # parameterized query - safe from SQLi
    query = "SELECT * FROM products WHERE name LIKE %s"
    return db.execute(query, ('%' + name + '%',)).fetchall()

```

### safe_5_xss (Python/Flask)
```
@app.route('/greet')
def greet():
    name = request.args.get('name', '')
    name = escape(name)  # HTML escape
    return f"<h1>Hello, {name}!</h1>"

```

### safe_6_crypto (Python)
```
import bcrypt
def hash_password(password):
    salt = bcrypt.gensalt(rounds=12)
    return bcrypt.hashpw(password.encode(), salt)

```

### safe_7_ssrf (Python)
```
import ipaddress
ALLOWED_DOMAINS = {'example.com', 'api.example.com'}
def fetch_url(url):
    parsed = urllib.parse.urlparse(url)
    if parsed.hostname not in ALLOWED_DOMAINS:
        raise ValueError("Domain not allowed")
    # also block internal IPs
    return requests.get(url, timeout=5)

```

### safe_8_jwt (Python)
```
import jwt
def verify_token(token):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
    except jwt.InvalidTokenError:
        return None

```

### safe_9_csrf (Python/Flask)
```
@app.route('/transfer', methods=['POST'])
@csrf_protect
@login_required
def transfer():
    amount = request.form.get('amount')
    # ... safe transfer logic

```

### safe_10_input (Python)
```
def parse_age(age_str):
    try:
        age = int(age_str)
        if age < 0 or age > 150:
            raise ValueError("Invalid age")
        return age
    except ValueError:
        return None

```


## 7.3 Cryptographic Weaknesses (10)

### crypto_1_md5 (Python) — Expected: ['MD5 (CWE-327)']
```
import hashlib
def hash_password(password):
    return hashlib.md5(password.encode()).hexdigest()

```

### crypto_2_sha1 (Python) — Expected: ['SHA1 (CWE-327)']
```
import hashlib
def hash_password(password):
    return hashlib.sha1(password.encode()).hexdigest()

```

### crypto_3_ecb (Python) — Expected: ['ECB mode (CWE-327)']
```
from Crypto.Cipher import AES
def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_ECB)
    return cipher.encrypt(pad(data))

```

### crypto_4_hardcoded_iv (Python) — Expected: ['Hardcoded IV (CWE-329)']
```
from Crypto.Cipher import AES
IV = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
def encrypt(data, key):
    cipher = AES.new(key, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(data))

```

### crypto_5_weak_random (Python) — Expected: ['Weak random (CWE-330)']
```
import random
def generate_token():
    return str(random.randint(100000, 999999))

```

### crypto_6_hardcoded_secret (Python) — Expected: ['Hardcoded secret (CWE-798)']
```
SECRET_KEY = "mysecret123"  # hardcoded
def sign(data):
    return hmac.new(SECRET_KEY.encode(), data.encode(), hashlib.sha256).hexdigest()

```

### crypto_7_plaintext_storage (Python) — Expected: ['Plaintext password storage (CWE-256)']
```
def save_password(username, password):
    # storing password in plaintext
    db.execute(f"INSERT INTO users (username, password) VALUES ('{username}', '{password}')")

```

### crypto_8_no_salt (Python) — Expected: ['No salt (CWE-916)']
```
import hashlib
def hash_password(password):
    # no salt - vulnerable to rainbow tables
    return hashlib.sha256(password.encode()).hexdigest()

```

### crypto_9_short_key (Python) — Expected: ['Short encryption key (CWE-326)']
```
KEY = b'shortkey'  # 8 bytes - too short
def encrypt(data):
    cipher = AES.new(KEY, AES.MODE_CBC, IV)
    return cipher.encrypt(pad(data))

```

### crypto_10_pickle (Python) — Expected: ['Unsafe deserialization (CWE-502)']
```
import pickle
def load_user_data(data):
    return pickle.loads(data)  # unsafe deserialization

```


## 7.4 Logic Bugs (10)

### logic_1_offbyone (Python) — Expected: ['Off-by-one']
```
def get_first_n(items, n):
    return items[:n+1]  # returns n+1 items instead of n

```

### logic_2_racey (Python) — Expected: ['Race condition (CWE-362)']
```
def transfer(from_acct, to_acct, amount):
        from_balance = get_balance(from_acct)
        if from_balance >= amount:
            # race condition - no lock
            set_balance(from_acct, from_balance - amount)
            to_balance = get_balance(to_acct)
            set_balance(to_acct, to_balance + amount)

```

### logic_3_nullderef (Python) — Expected: ['Null dereference']
```
def process_user(user_id):
    user = get_user(user_id)  # might return None
    return user.name  # null deref if user is None

```

### logic_4_int_overflow (C) — Expected: ['Integer overflow (CWE-190)']
```
int sum(int a, int b) {
    return a + b;  // no overflow check
}

```

### logic_5_deadlock (Python) — Expected: ['Deadlock (CWE-667)']
```
def transfer_mutex(from_acct, to_acct, amount):
    with lock[from_acct]:
        with lock[to_acct]:
            do_transfer(from_acct, to_acct, amount)
# deadlock if called as transfer(A, B) and transfer(B, A) concurrently

```

### logic_6_inf_loop (Python) — Expected: ['Infinite loop']
```
def find_first_even(nums):
    for n in nums:
        while n % 2 != 0:
            n += 1  # if all nums are odd and > 0, infinite loop on last
        return n

```

### logic_7_uninit (C) — Expected: ['Uninitialized variable (CWE-457)']
```
int compute() {
    int x;  // uninitialized
    return x * 2;
}

```

### logic_8_division (Python) — Expected: ['Division by zero']
```
def safe_divide(a, b):
    return a / b  # no zero check

```

### logic_9_format_string (C) — Expected: ['Format string (CWE-134)']
```
void log_msg(char* user_input) {
    printf(user_input);  // format string vuln
}

```

### logic_10_resource_leak (Python) — Expected: ['Resource leak']
```
def read_file(path):
    f = open(path)
    data = f.read()
    # missing f.close()
    return data

```

