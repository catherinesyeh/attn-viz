# attn-viz

### install instructions
1. clone repo:
```
git clone https://github.com/catherinesyeh/attn-viz.git
```

2. navigate into folder:
```
cd attn-viz
```

3. create .env file: replace **[TOKEN]** with token from Catherine
```
touch .env
echo "API_TOKEN=[TOKEN]" > .env
```

4. start app:
```
source env/bin/activate && honcho -f ProcfileHoncho start
```

5. view in browser: [http://localhost:8561/](http://localhost:8561/)

*Note: data may take 1-2 minutes to load initially.*
