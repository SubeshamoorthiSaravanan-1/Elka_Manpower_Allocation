# 🚀 Deploy to Render.com - Complete Guide

## ⚡ 5-Minute Setup

### **Step 1: Prepare GitHub Repository**
```bash
# If not already a git repo
git init
git add .
git commit -m "Initial Elkayem deployment"
git branch -M main

# Push to GitHub
# (Create repo on GitHub first, then push)
git remote add origin https://github.com/YOUR-USERNAME/elkayem.git
git push -u origin main
```

### **Step 2: Create Render Account**
1. Go to **[render.com](https://render.com)**
2. Click **Sign Up** → Choose **GitHub**
3. Authorize GitHub access
4. You're in! ✅

### **Step 3: Deploy Your App**
1. Click **New +** → **Web Service**
2. Select your **elkayem** GitHub repo
3. Fill in details:
   ```
   Name: elkayem-api
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python server_advanced.py
   Plan: Free
   ```
4. Click **Create Web Service**
5. Wait 2-3 minutes for deployment ✅

### **Step 4: Access Your App**
- **URL**: `https://elkayem-api.onrender.com`
- Open in browser → Login with `admin` / `admin123`
- Done! 🎉

---

## 📝 Configuration Details

### **Environment Variables** (Optional)
Add these in Render Dashboard → Settings → Environment:

```
PORT=8080
JWT_SECRET=your-production-secret-key-here
DATABASE_PATH=/var/data/elkayem.db
```

### **Persistent Storage** (Database)**
Render.com free tier includes **5 GB** storage.

**Database will be stored at:**
- `/var/data/elkayem.db` (survives restarts)
- Or modify `server_advanced.py` to use Render's database

### **Auto-Deploy**
✅ Any push to GitHub → Auto-deploys to Render.com

---

## 🔒 Security Checklist

Before going live:

- [ ] Change `JWT_SECRET` in `server_advanced.py`
- [ ] Change default admin password
- [ ] Use HTTPS (Render provides free SSL)
- [ ] Set up environment variables in Render Dashboard

---

## 📊 Monitoring

In Render Dashboard:
- **Logs** → View real-time server output
- **Metrics** → CPU, Memory, Bandwidth usage
- **Events** → Deployment history

---

## 💾 Backup & Database

### **Export Database from Render**
```bash
# SSH into your Render service (if enabled)
# Or download via SFTP using credentials from Render Dashboard
```

### **Upload Backup**
```bash
# Keep elkayem.db in repo (or gitignore it)
# Render stores it in persistent storage
```

---

## 🆘 Troubleshooting

### **App won't start?**
- Check **Logs** in Render Dashboard
- Verify `start_command` is correct
- Check Python version compatibility

### **Database not persisting?**
- Ensure path is `/var/data/` or equivalent
- Check `elkayem.db` isn't in `.gitignore` if you want to version it
- Use Render's PostgreSQL addon (paid tier)

### **Port issues?**
- Render assigns port dynamically
- Modify `server_advanced.py`:
```python
PORT = int(os.environ.get('PORT', 8080))
```

---

## 🎯 Next Steps

1. ✅ Push to GitHub
2. ✅ Connect to Render.com
3. ✅ Share URL with users
4. ✅ Monitor in Render Dashboard

**Your free tier supports:**
- 100+ daily active users
- Unlimited bandwidth
- Auto-restarts on crash
- Free SSL/HTTPS

---

## 📞 Need Help?

- **Render Docs**: https://render.com/docs
- **Status Page**: https://status.render.com
- **Support**: https://support.render.com
