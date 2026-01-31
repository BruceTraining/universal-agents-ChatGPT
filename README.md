# Demo: Building a Tech Support Classifier in OpenAI Agent Builder

In this hands-on demo, you'll use the OpenAI Agent Builder to create a no-code customer support routing system. You'll configure a **Classifier** that automatically categorizes incoming customer messages and routes them to the appropriate specialized agent.

## What You'll Build

By the end of this demo, you'll have a fully functional multi-agent support system that:

- **Classifies** incoming customer messages into four categories: Billing, Tech-Support, Website, and General
- **Routes** each message to a specialized responder agent trained for that category
- **Generates** contextually appropriate responses with reference/ticket numbers
- **Handles** edge cases where messages may be ambiguous

This pattern is foundational for building production-ready customer support automation, help desk systems, and any application requiring intelligent request routing.

---

## Step 1: Create the Classifier

Create a new Classifier with **four categories**:

| Category | Description |
|----------|-------------|
| `billing` | Payment, refunds, invoices, pricing issues |
| `tech-support` | Hardware/software problems with laptops |
| `website` | Issues accessing or using the company website |
| `general` | Partnership inquiries, job questions, feedback, etc. |

---

## Step 2: Add Few-Shot Examples

Provide the following training examples to help the classifier accurately categorize messages.

### Billing Examples

- I was charged twice for my laptop order
- Can I get a refund for the laptop I returned last week?
- My credit card was declined but the order still went through
- I need a copy of my purchase receipt for warranty purposes
- How do I get an invoice for my company's laptop purchase?
- I bought my laptop from a reseller but they charged me more than the listed price
- When will my refund be processed for the cancelled order?
- I was supposed to get a student discount but I was charged full price
- How do I claim the cashback promotion for my laptop purchase?
- I need to update the billing address on my order

### Tech-Support Examples

- My laptop won't turn on even when plugged in
- The touchpad stopped working after the latest Windows 11 update
- My laptop screen is flickering intermittently
- The battery drains very quickly even when the laptop is idle
- I'm getting a blue screen error with the code DRIVER_IRQL_NOT_LESS_OR_EQUAL
- The keyboard backlight isn't working anymore
- My laptop overheats and shuts down when I play games
- The webcam isn't being detected by Windows 11
- I can't connect to WiFi after updating Windows 11
- The speakers make a crackling sound when playing audio

### Website Examples

- I can't log in to my account on your website
- The checkout page isn't loading
- Your website looks broken on my mobile phone
- I can't find the pricing page
- The links in your footer are broken
- Your website is very slow to load
- I'm having trouble navigating to my account settings
- The images on your homepage aren't displaying
- I can't complete the signup form - the submit button doesn't work
- Your site doesn't work properly in Safari

### General Examples

- I'm interested in becoming an authorized reseller for your laptops
- Do you have any job openings in your engineering department?
- Can you tell me about the sustainability practices in your manufacturing?
- I'd like to schedule a demo of your business laptop lineup for my company
- How can I contact your PR team for a media inquiry?
- Do you offer bulk discounts for educational institutions?
- I have some feedback about the design of your latest laptop model
- Where are your laptops manufactured?
- Does your company have a recycling program for old laptops?
- I want to learn more about your corporate laptop leasing options

---

## Step 3: Create the Responder Agents

Create four agents, one for each category. Use **GPT 5.2 mini** as the model for all agents.

### Billing Responder

**Name:** `Billing Responder`  
**Model:** `GPT 5.2 mini`  
**Instructions:**

```
You are a friendly billing support specialist for a laptop manufacturer. The customer has a billing-related question about their laptop purchase.

Your response should:
1. Acknowledge their billing concern warmly
2. Provide helpful information about common billing topics (order charges, refunds, invoices, promotional pricing, reseller pricing issues)
3. If they purchased from a reseller, explain that billing disputes with resellers need to be handled through the reseller, but offer to verify the correct retail price
4. If you can't fully resolve their issue, let them know a billing specialist will follow up within 24 hours
5. Always include a reference number in this format: "Reference: BILL-" followed by 6 random digits

Keep your tone professional but friendly. Be concise but thorough.
```

---

### Tech-Support Responder

**Name:** `Tech-Support Responder`  
**Model:** `GPT 5.2 mini`  
**Instructions:**

```
You are a helpful technical support specialist for a laptop manufacturer. The customer has a technical issue with their Windows 11 laptop.

Your response should:
1. Acknowledge their technical issue with empathy
2. Ask clarifying questions if needed (laptop model, when the issue started, any recent updates or changes)
3. Provide initial troubleshooting steps specific to Windows 11 laptops, such as:
   - Updating or rolling back drivers
   - Running Windows troubleshooters
   - Checking Device Manager for hardware issues
   - BIOS updates if relevant
   - Power cycling or hard reset procedures
4. If the issue sounds like a hardware defect, explain the warranty claim process
5. Let them know that if the issue persists, a technical specialist will investigate further
6. Always include a ticket number in this format: "Ticket: TECH-" followed by 6 random digits

Be patient and clear. Avoid jargon. Guide them step by step.
```

---

### Website Responder

**Name:** `Website Responder`  
**Model:** `GPT 5.2 mini`  
**Instructions:**

```
You are a website support specialist helping customers with issues accessing or using our website.

Your response should:
1. Acknowledge their website issue with understanding
2. Ask about their browser, device, and what they were trying to do
3. Suggest common fixes: clearing cache, trying a different browser, checking internet connection
4. If the issue sounds like a bug on our end, assure them you'll report it to the web team
5. Always include a reference number in this format: "Reference: WEB-" followed by 6 random digits

Be helpful and patient. Many users may not be technically savvy.
```

---

### General Responder

**Name:** `General Responder`  
**Model:** `GPT 5.2 mini`  
**Instructions:**

```
You are a friendly customer support representative for a laptop manufacturer handling general inquiries.

Your response should:
1. Thank them for reaching out
2. Address their question or concern as best you can
3. For reseller/partnership inquiries: let them know the partnerships team will be in touch within 2 business days
4. For job inquiries: direct them to your careers page at [company website]/careers
5. For bulk/educational/corporate pricing inquiries: let them know a sales representative will contact them within 1 business day
6. For press/media inquiries: provide the PR team contact email
7. For product feedback: thank them sincerely and assure them it will be shared with the product design team
8. For sustainability/recycling questions: provide brief information and offer to send detailed documentation
9. Always include a reference number in this format: "Reference: GEN-" followed by 6 random digits

Be warm, helpful, and professional.
```

---

## Step 4: Test Your Workflow

Open the test/playground panel and try these messages to verify your classifier and agents are working correctly.

### Test 1 — Billing

**Input:**
> I was charged twice for my laptop order last week. Can I get a refund for the duplicate charge?

**Expected:** Routes to **Billing Responder**

---

### Test 2 — Tech-Support

**Input:**
> My laptop screen keeps flickering and then goes black. I'm running Windows 11 and it started after the last update.

**Expected:** Routes to **Tech-Support Responder**

---

### Test 3 — Website

**Input:**
> I can't log in to your website to track my order. The page just keeps spinning.

**Expected:** Routes to **Website Responder**

---

### Test 4 — General

**Input:**
> Hi, I'm the IT director at a school district and I'm interested in bulk pricing for student laptops.

**Expected:** Routes to **General Responder**

---

### Test 5 — Edge Case (Ambiguous)

**Input:**
> I ordered a laptop but it arrived with a cracked screen and I need help getting a replacement.

**Discussion:** This message is intentionally ambiguous—it could reasonably route to either Billing (replacement/refund) or Tech-Support (hardware issue). Use this to discuss how classifiers handle edge cases and the importance of well-designed few-shot examples.

---

## Summary

You've now built a complete multi-agent customer support system using the OpenAI Agent Builder:

1. ✅ Created a classifier with four categories
2. ✅ Trained it with few-shot examples
3. ✅ Built specialized responder agents for each category
4. ✅ Tested the end-to-end workflow

This same pattern can be extended to handle more categories, integrate with external tools, or connect to live customer support systems.
