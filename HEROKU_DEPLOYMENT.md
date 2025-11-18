# Heroku Deployment Guide

This guide provides instructions for deploying the Stock Trading Decision Support System to Heroku.

## Prerequisites

- [Heroku CLI](https://devcenter.heroku.com/articles/heroku-cli) installed
- Git installed
- Heroku account created
- Project repository cloned locally

## Quick Deployment

### 1. Login to Heroku

```bash
heroku login
```

### 2. Create a New Heroku App

```bash
heroku create your-app-name
# Or let Heroku generate a random name:
# heroku create
```

### 3. Set Environment Variables

Configure the required environment variables:

```bash
# Application settings
heroku config:set APP_ENV=production
heroku config:set DEBUG=False
heroku config:set LOG_LEVEL=INFO

# API configuration
heroku config:set API_HOST=0.0.0.0

# Trading configuration
heroku config:set INITIAL_CAPITAL=100000
heroku config:set MAX_POSITION_SIZE=0.05
heroku config:set STOP_LOSS_PERCENT=0.02
heroku config:set TAKE_PROFIT_PERCENT=0.05

# Data paths (Heroku ephemeral filesystem)
heroku config:set DATA_RAW_PATH=/tmp/data/raw
heroku config:set DATA_PROCESSED_PATH=/tmp/data/processed
heroku config:set MODEL_SAVED_PATH=/tmp/models/saved_models
heroku config:set LOG_PATH=/tmp/logs
```

### 4. Deploy to Heroku

```bash
git push heroku main
# Or if deploying from a different branch:
# git push heroku your-branch:main
```

### 5. Scale the Web Dyno

```bash
heroku ps:scale web=1
```

### 6. Open the Application

```bash
heroku open
```

## Deployment from Specific Branch

If you're working on a feature branch like `claude/deploy-code-*`:

```bash
# Push the branch to Heroku
git push heroku claude/deploy-code-01Ut69EwuiGB1ikoJN8ZMm57:main
```

## Environment Configuration

### Required Environment Variables

- `APP_ENV`: Application environment (production)
- `API_HOST`: API host (0.0.0.0)

### Optional Environment Variables

You can configure additional variables as needed. See `.env.example` for all available options.

Example:

```bash
heroku config:set BUY_THRESHOLD=0.02
heroku config:set SELL_THRESHOLD=-0.01
heroku config:set SIGNAL_CONFIDENCE_MIN=0.6
```

## Post-Deployment

### 1. Check Application Logs

```bash
heroku logs --tail
```

### 2. Verify API Health

```bash
curl https://your-app-name.herokuapp.com/health
```

Expected response:
```json
{
  "status": "healthy",
  "version": "0.1.0"
}
```

### 3. Test API Endpoints

```bash
# Get prediction
curl https://your-app-name.herokuapp.com/api/v1/predictions/AAPL

# Get trading signal
curl https://your-app-name.herokuapp.com/api/v1/signals/AAPL

# Check monitoring health
curl https://your-app-name.herokuapp.com/api/v1/monitoring/health
```

## Important Notes

### Ephemeral Filesystem

Heroku uses an ephemeral filesystem, which means:
- Files written to disk are temporary
- Files are deleted when the dyno restarts
- Use `/tmp` directory for temporary storage

**Solutions:**
1. **For Data Storage**: Use Heroku Add-ons (PostgreSQL, AWS S3)
2. **For Model Storage**: Store models in S3 or similar cloud storage
3. **For Logs**: Use Heroku's logging system or external log management

### Data Persistence

For production use, you should:

1. **Store historical data in a database**:
   ```bash
   # Add PostgreSQL
   heroku addons:create heroku-postgresql:mini
   ```

2. **Store models in cloud storage**:
   - Use AWS S3 for model storage
   - Configure environment variables for S3 access

3. **Use external logging**:
   ```bash
   # Add Papertrail for log management
   heroku addons:create papertrail:choklad
   ```

### Model Training

Since model training is computationally intensive:

1. **Train models locally** or on a separate compute instance
2. **Upload trained models** to cloud storage (S3)
3. **Download models** on application startup

### Scaling

Adjust dyno resources based on your needs:

```bash
# Scale to multiple dynos
heroku ps:scale web=2

# Upgrade to a larger dyno
heroku ps:type web=standard-1x
```

## Monitoring

### View Application Metrics

```bash
heroku metrics
```

### Monitor Dyno Status

```bash
heroku ps
```

### Access Heroku Dashboard

Visit: https://dashboard.heroku.com/apps/your-app-name

## Troubleshooting

### Application Crashes

Check logs:
```bash
heroku logs --tail
```

Common issues:
- Missing environment variables
- Port binding errors (ensure using `$PORT`)
- Memory limits exceeded

### Slow Performance

- Consider upgrading dyno type
- Optimize model loading
- Use caching where appropriate

### Build Failures

Check build logs:
```bash
heroku logs --tail
```

Common issues:
- Missing dependencies in `requirements.txt`
- Incompatible Python version
- Build timeout (complex dependencies)

## Development vs Production

### Development Setup

```bash
heroku config:set APP_ENV=development
heroku config:set DEBUG=True
heroku config:set LOG_LEVEL=DEBUG
```

### Production Setup

```bash
heroku config:set APP_ENV=production
heroku config:set DEBUG=False
heroku config:set LOG_LEVEL=INFO
heroku config:set API_WORKERS=4
```

## Database Setup (Optional)

If you need persistent storage:

```bash
# Add PostgreSQL
heroku addons:create heroku-postgresql:mini

# Get database URL
heroku config:get DATABASE_URL

# Set database type
heroku config:set DATABASE_TYPE=postgresql
```

## Advanced Configuration

### Custom Buildpacks

The app uses the Python buildpack by default. If you need additional buildpacks:

```bash
heroku buildpacks:add --index 1 heroku/python
```

### Background Workers

For running background tasks (model training, data updates):

Add a worker process to `Procfile`:
```
worker: python scripts/background_worker.py
```

Then scale the worker:
```bash
heroku ps:scale worker=1
```

### Scheduler

For periodic tasks:

```bash
heroku addons:create scheduler:standard
heroku addons:open scheduler
```

Add tasks like:
- `python scripts/download_historical_data.py`
- `python scripts/retrain_models.py`

## Cost Optimization

- Use Eco dynos for development ($5/month)
- Use Hobby dynos for small production apps ($7/month)
- Scale down when not in use
- Monitor dyno hours

## Security

### Enable HTTPS

Heroku automatically provides HTTPS for all apps.

### Environment Variables

Never commit sensitive data:
- Use `heroku config:set` for secrets
- Never commit `.env` files
- Keep API keys in Heroku config

### API Security

Consider adding:
- API key authentication
- Rate limiting
- CORS configuration

## Support

For issues with Heroku deployment:
- [Heroku Dev Center](https://devcenter.heroku.com/)
- [Heroku Status](https://status.heroku.com/)
- [Heroku Support](https://help.heroku.com/)

For application-specific issues:
- Check application logs
- Review API endpoints
- Verify environment configuration

## Next Steps

1. Set up database for data persistence
2. Configure cloud storage for models
3. Implement proper logging and monitoring
4. Add API authentication
5. Set up CI/CD pipeline
6. Configure domain name (if needed)

## Useful Commands

```bash
# View all config variables
heroku config

# Restart the application
heroku restart

# Run a one-off command
heroku run python --version

# Open Rails console (if applicable)
heroku run bash

# View add-ons
heroku addons

# View app info
heroku info
```

## Example: Complete Deployment

```bash
# 1. Create app
heroku create stock-trading-api

# 2. Set environment
heroku config:set APP_ENV=production DEBUG=False LOG_LEVEL=INFO

# 3. Deploy
git push heroku main

# 4. Scale
heroku ps:scale web=1

# 5. Check status
heroku ps
heroku logs --tail

# 6. Test
curl https://stock-trading-api.herokuapp.com/health

# 7. Open app
heroku open
```

## Conclusion

Your Stock Trading Decision Support System is now deployed on Heroku! The API is accessible and ready to provide predictions and trading signals.

Remember:
- Monitor your application regularly
- Keep dependencies updated
- Use appropriate dyno sizes
- Implement proper data persistence for production
- Follow security best practices
