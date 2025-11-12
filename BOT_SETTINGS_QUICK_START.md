# Bot Settings - Quick Start Guide

## For End Users

### Configure Your Bot in 3 Steps

#### Step 1: Navigate to Bot Settings
1. Log into your Weaver dashboard
2. Click the **"Bot Settings"** tab
3. You'll see a simple form asking about your business

#### Step 2: Fill Out Your Business Information

**Required Fields:**
- **Business/Product Name** - e.g., "Acme Corp", "MyProduct"
- **Industry** - e.g., "SaaS", "E-commerce", "Healthcare"
- **What does your business do?** - 2-3 sentence description
- **Bot Personality** - Choose from dropdown:
  - Professional & Polished
  - Friendly & Conversational
  - Technical & Precise
  - Casual & Approachable
  - Formal & Academic
- **Primary Goal** - What should the bot help with?

**Optional:**
- **Special Instructions** - Any specific guidelines

#### Step 3: Generate and Save
1. Click **"Generate Bot Configuration"** (takes 1-2 seconds)
2. Review the generated prompt - you can edit it if needed
3. Click **"Save & Activate Bot"**
4. Done! Your bot now has a custom personality

### Example Scenarios

#### 🏢 SaaS Product Support
```
Business Name: CloudSync
Industry: SaaS
Description: We provide cloud file synchronization for businesses. 
  Our platform syncs files across devices in real-time with enterprise 
  security.
Tone: Professional & Polished
Goal: Answer customer questions about features, pricing, and integrations
```

#### 🛒 E-commerce Store
```
Business Name: Artisan Market
Industry: E-commerce
Description: Online marketplace for handcrafted goods. We connect 
  artisans with buyers worldwide, offering unique, handmade products.
Tone: Friendly & Conversational
Goal: Help customers find products and answer shipping/return questions
Special: Always mention our 30-day satisfaction guarantee
```

#### 💻 Technical Documentation
```
Business Name: DevTools API
Industry: Developer Tools
Description: RESTful API for payment processing. We offer simple 
  integration, comprehensive documentation, and 99.99% uptime SLA.
Tone: Technical & Precise
Goal: Provide accurate API documentation and code examples
Special: Always encourage checking API reference for latest endpoints
```

---

## For Developers

### API Endpoints

#### Generate System Prompt
```bash
POST /v1/tenants/{tenant_id}/bot/generate-prompt
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "business_name": "Acme Corp",
  "industry": "E-commerce",
  "description": "We sell premium widgets online with fast shipping",
  "tone": "friendly",
  "primary_goal": "Help customers find the right products",
  "special_instructions": "Always mention free shipping over $50"
}

# Response
{
  "system_prompt": "You are Acme Corp's friendly shopping assistant...",
  "business_info": { ... }
}
```

#### Update Bot Configuration
```bash
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "system_prompt": "Your custom prompt or generated prompt",
  "business_info": {
    "business_name": "...",
    "industry": "...",
    ...
  }
}

# Response
{
  "tenant_id": "...",
  "name": "Your Bot",
  "system_prompt": "...",
  "business_info": {...},
  "using_default_prompt": false,
  "created_at": "2024-01-01T00:00:00",
  "updated_at": "2024-01-01T00:00:00"
}
```

#### Revert to Default Prompt
```bash
PUT /v1/tenants/{tenant_id}/bot
Authorization: Bearer YOUR_JWT_TOKEN
Content-Type: application/json

{
  "system_prompt": ""
}
```

### Frontend Integration

```typescript
import { useGenerateSystemPrompt, useUpdateBotConfig } from '@/hooks/useBot'

function MyComponent() {
  const generateMutation = useGenerateSystemPrompt(tenantId)
  const updateMutation = useUpdateBotConfig(tenantId)
  
  const handleGenerate = async () => {
    const result = await generateMutation.mutateAsync({
      businessName: "Acme Corp",
      industry: "E-commerce",
      description: "...",
      tone: "friendly",
      primaryGoal: "Help customers",
      specialInstructions: "..."
    })
    console.log(result.system_prompt)
  }
  
  const handleSave = async (prompt: string) => {
    await updateMutation.mutateAsync({
      system_prompt: prompt,
      business_info: { ... }
    })
  }
}
```

### Database Schema

```sql
-- Stored in bots.config_json (JSONB)
{
  "system_prompt": "You are...",
  "business_info": {
    "business_name": "Acme Corp",
    "industry": "E-commerce",
    "description": "...",
    "tone": "friendly",
    "primary_goal": "...",
    "special_instructions": "..."
  }
}
```

### Testing the Feature

```bash
# Start dev environment
./start-dev.sh

# Backend tests
cd backend
pytest tests/test_prompt_generator.py -v

# Frontend tests
cd frontend
npm test -- BotSettingsTab

# Manual test in UI
# 1. Navigate to http://localhost:3000
# 2. Sign in
# 3. Go to "Bot Settings" tab
# 4. Fill form and generate
# 5. Save configuration
# 6. Go to "API Keys" tab -> "Test Your Bot"
# 7. Verify bot uses new personality
```

---

## Tips & Best Practices

### Writing Effective Descriptions
✅ **Good:**
> "We provide cloud-based project management software for remote teams. 
> Our platform includes task tracking, time management, and team collaboration 
> features."

❌ **Too Vague:**
> "We help businesses be more productive."

### Choosing the Right Tone

| If your business is... | Choose |
|------------------------|--------|
| B2B Enterprise SaaS | Professional |
| Consumer mobile app | Friendly |
| Developer tools/API | Technical |
| Lifestyle/social app | Casual |
| Legal/healthcare | Formal |

### Special Instructions Examples
- "Always include a disclaimer about not providing medical advice"
- "Mention our 24/7 support for urgent issues"
- "Use emojis occasionally 😊"
- "Link to docs.example.com for technical details"
- "Direct pricing questions to sales team"

### When to Regenerate
- Changing your target audience
- Launching new features
- Rebranding
- Feedback indicates wrong tone
- Low confidence queries on specific topics

---

## FAQ

**Q: Can I write my own prompt instead?**  
A: Yes! Just edit the generated prompt before saving, or write one from scratch in the text area.

**Q: How long does generation take?**  
A: Typically 1-2 seconds using Gemini's fast model.

**Q: Can I regenerate if I don't like the result?**  
A: Absolutely! Click "Regenerate" as many times as you want. Each generation will be slightly different.

**Q: Does changing the prompt affect existing conversations?**  
A: Yes, all new queries will use the updated prompt immediately. Past conversations are not changed.

**Q: Can I save multiple versions?**  
A: Currently, you can only have one active prompt per bot. The business_info is saved so you can regenerate later.

**Q: What if I want to use the default prompt again?**  
A: Save an empty string as the system_prompt - the bot will revert to using the default.

**Q: Is there a character limit?**  
A: The generated prompts are typically 2-4 paragraphs (~300-600 words). You can edit to make them longer or shorter.

---

## Support

Need help configuring your bot?
- 📧 Email: support@weaver.com
- 📖 Full docs: [BUSINESS_INFO_PROMPT_GENERATION.md](./BUSINESS_INFO_PROMPT_GENERATION.md)
- 💬 Chat: Available in dashboard

---

**Last Updated:** November 2024  
**Version:** 1.0

