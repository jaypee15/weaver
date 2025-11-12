# Business Info to System Prompt Generation

## Overview

Instead of requiring users to write system prompts directly, Weaver now uses AI to generate optimal system prompts based on simple business information. This makes bot configuration accessible to all users, regardless of their prompt engineering skills.

## Architecture

### Backend Components

#### 1. Prompt Generator Service
**File:** `backend/app/services/prompt_generator.py`

Uses Gemini LLM to generate system prompts from business information:
- **Model:** `gemini-1.5-flash-8b` (fast and cost-effective)
- **Temperature:** `0.7` (slightly higher for creativity)
- **Input:** Business name, industry, description, tone, primary goal, special instructions
- **Output:** Production-ready system prompt (2-4 paragraphs)

#### 2. API Endpoints

**Generate Prompt:**
```
POST /v1/tenants/{tenant_id}/bot/generate-prompt
```
- **Input:** `BusinessInfoRequest` (business details)
- **Output:** `GeneratedPromptResponse` (system prompt + business info)
- **Auth:** Requires admin/owner role

**Update Bot Config:**
```
PUT /v1/tenants/{tenant_id}/bot
```
- **Input:** `BotConfigUpdate` (system_prompt, business_info)
- **Output:** `BotSettingsResponse` (updated configuration)
- **Auth:** Requires admin/owner role
- **Note:** Empty string for `system_prompt` reverts to default

#### 3. Database Storage

Bot configuration stored in `bots.config_json` (JSONB):
```json
{
  "system_prompt": "You are TechDocs Pro's AI assistant...",
  "business_info": {
    "business_name": "TechDocs Pro",
    "industry": "SaaS",
    "description": "...",
    "tone": "technical",
    "primary_goal": "...",
    "special_instructions": "..."
  }
}
```

### Frontend Components

#### 1. BotSettingsTab Component
**File:** `frontend/src/components/dashboard/BotSettingsTab.tsx`

User-friendly form with:
- **Business Name** (required)
- **Industry** (required)
- **Description** (required, 2-3 sentences)
- **Tone Selection** (dropdown):
  - Professional & Polished
  - Friendly & Conversational
  - Technical & Precise
  - Casual & Approachable
  - Formal & Academic
- **Primary Goal** (required)
- **Special Instructions** (optional)

#### 2. React Query Hooks
**File:** `frontend/src/hooks/useBot.ts`

- `useGenerateSystemPrompt(tenantId)` - Calls generation endpoint
- `useUpdateBotConfig(tenantId)` - Saves configuration
- Auto-invalidates cache on update

## User Flow

### Step 1: Fill Business Information
```
User navigates to "Bot Settings" tab
↓
Fills out simple form (no prompt engineering needed)
↓
Clicks "Generate Bot Configuration"
```

### Step 2: Review Generated Prompt
```
AI generates system prompt (1-2 seconds)
↓
User reviews prompt in editable text area
↓
Can edit, regenerate, or cancel
```

### Step 3: Save and Activate
```
User clicks "Save & Activate Bot"
↓
Configuration saved to database
↓
Bot immediately uses new system prompt
↓
Business info stored for future regeneration
```

## Example Usage

### Input:
```
Business Name: TechDocs Pro
Industry: SaaS / Technical Documentation
Description: We provide automated technical documentation generation 
  for software teams. Our platform helps developers create and maintain 
  up-to-date API docs, user guides, and internal wikis.
Tone: Technical & Precise
Primary Goal: Help users understand our platform features and troubleshoot issues
Special Instructions: Always encourage users to check our API reference 
  for code examples
```

### Generated Output:
```
You are TechDocs Pro's AI documentation assistant, specialized in helping 
software teams understand and utilize our automated technical documentation 
platform. Your role is to provide precise, technically accurate information 
about our features, integrations, and best practices.

When answering questions, maintain a technical and precise tone, using 
industry-standard terminology. Your primary goal is to help users understand 
platform features and resolve any issues they encounter. Always base your 
responses on the provided documentation context, and cite specific sections 
or features when relevant.

If the documentation doesn't contain sufficient information to answer a 
question, clearly state this limitation and suggest users check our 
comprehensive API reference at docs.techdocspro.com/api for detailed code 
examples and implementation guides. For complex technical issues or feature 
requests, recommend contacting our engineering team directly.

Remember to highlight relevant integrations, automation capabilities, and 
best practices that can help users maximize the value of TechDocs Pro for 
their development workflow.
```

## Benefits

### For Users
✅ **No prompt engineering skills required**  
✅ **Consistent, high-quality prompts**  
✅ **Fast generation (1-2 seconds)**  
✅ **Editable for fine-tuning**  
✅ **Clear, simple form interface**  

### For Developers
✅ **Leverages existing LLM infrastructure**  
✅ **Stored business info for regeneration**  
✅ **Easy to extend with more fields**  
✅ **Maintains backward compatibility**  

## Technical Details

### Meta-Prompt Design

The system uses a carefully crafted "meta-prompt" that instructs the LLM to:
1. Define AI's role clearly
2. Match the specified tone
3. Focus on the primary goal
4. Include context-based answering guidelines
5. Handle insufficient information gracefully
6. Incorporate special instructions
7. Output clean, production-ready text (no markdown)

### Temperature Setting

`temperature=0.7` provides a balance between:
- **Creativity** - Varied, engaging prompts
- **Consistency** - Reliable structure and format
- **Accuracy** - Stays true to input requirements

### Cost Optimization

Using `gemini-1.5-flash-8b`:
- **Speed:** ~1-2 seconds per generation
- **Cost:** Minimal (a few tokens per request)
- **Quality:** Excellent for this use case

## Configuration Options

### Tone Personality Matrix

| Tone | Description | Use Case |
|------|-------------|----------|
| **Professional** | Polished, business-appropriate | Enterprise SaaS, B2B services |
| **Friendly** | Warm, conversational, approachable | Consumer apps, community platforms |
| **Technical** | Precise, detailed, technically accurate | Developer tools, APIs, infrastructure |
| **Casual** | Relaxed, informal, easy-going | Social apps, lifestyle products |
| **Formal** | Academic, authoritative, structured | Legal, healthcare, education |

### Special Instructions Examples

- "Always include a disclaimer about not providing medical/legal advice"
- "Mention our 24/7 support team for urgent issues"
- "Use emojis to make responses more engaging"
- "Include links to relevant documentation sections"
- "Always suggest contacting sales for pricing questions"

## Future Enhancements

### Potential Additions
1. **Multi-language support** - Generate prompts in different languages
2. **Industry templates** - Pre-filled examples for common industries
3. **A/B testing** - Compare different prompt variations
4. **Prompt versioning** - Track changes over time
5. **Analytics** - See how prompt changes affect bot performance
6. **Import/Export** - Share successful prompts with team

### Advanced Features
- **Prompt library** - Community-shared templates
- **Auto-optimization** - Refine prompts based on low-confidence queries
- **Tone analysis** - Verify bot responses match intended tone
- **Compliance checks** - Ensure prompts meet industry regulations

## Testing

### Manual Testing Checklist
- [ ] Generate prompt with all required fields
- [ ] Test each tone option (professional, friendly, technical, casual, formal)
- [ ] Edit generated prompt before saving
- [ ] Regenerate multiple times (verify variations)
- [ ] Save configuration and verify persistence
- [ ] Test with empty system_prompt (reverts to default)
- [ ] Query bot and verify it uses new prompt
- [ ] Test special instructions are incorporated

### API Testing
```bash
# Generate prompt
curl -X POST http://localhost:8000/v1/tenants/{tenant_id}/bot/generate-prompt \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "business_name": "Acme Corp",
    "industry": "E-commerce",
    "description": "We sell widgets online",
    "tone": "friendly",
    "primary_goal": "Help customers find products",
    "special_instructions": "Always be positive"
  }'

# Update bot config
curl -X PUT http://localhost:8000/v1/tenants/{tenant_id}/bot \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "system_prompt": "Your custom prompt here",
    "business_info": {...}
  }'
```

## Monitoring

### Metrics to Track
- **Generation latency** - Time to generate prompts
- **Adoption rate** - % of users using this feature
- **Regeneration rate** - How often users regenerate
- **Edit rate** - How often users edit before saving
- **Bot performance** - Correlation between custom prompts and query success

### Logging
```python
# In prompt_generator.py
logger.info(f"Generated prompt for tenant {tenant_id}, tone: {tone}, length: {len(system_prompt)}")

# In routes.py
logger.info(f"Tenant {tenant_id} updated bot config")
```

## Troubleshooting

### Common Issues

**Prompt too generic?**
- Add more detail to the description
- Use special instructions for specific guidelines
- Try regenerating with a different tone

**Prompt too long?**
- Simplify the description
- Reduce special instructions
- The LLM is designed to output 2-4 paragraphs

**Bot not using new prompt?**
- Verify save was successful (check response)
- Check bot config in database: `SELECT config_json FROM bots WHERE tenant_id = '...'`
- Restart API container if needed

**Generation fails?**
- Check Gemini API key is valid
- Verify network connectivity
- Check API logs for specific errors

## Conclusion

This feature dramatically lowers the barrier to entry for bot customization. Users can now create professional, tailored bot personalities in minutes without any technical knowledge of prompt engineering.

The combination of:
- Simple, guided form
- AI-powered generation
- Editable output
- Instant activation

...makes Weaver's bot configuration one of the most user-friendly in the industry.

