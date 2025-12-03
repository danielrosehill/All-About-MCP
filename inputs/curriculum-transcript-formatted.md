# MCP Curriculum - Formatted Transcript

*Transcribed from curriculum.mp3 using local Whisper*

---

## Preamble

Today has been a day where I've done a lot of these audio recordings for use in repositories, which is a method I've been exploring. I figured I might as well use this to quickly define the curriculum, because I'd love to generate this overnight and then tomorrow spend some time listening to it.

This is the curriculum for an AI-generated course book providing an overview to MCP. I was looking at videos on MCP on YouTube and the whole idea here is that you frequently run into an endless stream of the same content - "introduction to MCP" - that isn't really useful for me at the moment. I have specific questions. To organize this properly and somewhat coherently, I'll describe the approximate structure to be followed in the curriculum.

---

## Part 1: What is MCP?

### Origins and History

Let's start with: what is MCP? Model Context Protocol. MCP is really not that old - in fact, we just had the one-year birthday of MCP. I'm not overly familiar with its actual origin story, other than knowing that Anthropic came up with it. But I'm sure there's more to it than that - I'm sure it was more than one person at Anthropic who came up with the idea or worked on its initial implementation. That's important ground to cover.

### Alternative Approaches and Controversy

It's also important to cover alternative approaches. Like any advance in technology, there have been debates and differences of opinion regarding what actually is the best way to allow agents to act upon external systems. I know from seeing threads on Twitter that there is some controversy around MCP. Some people say "this is the most ridiculous, bloated protocol - unnecessary. It's just an API. Why do we need another thing around an API?" That criticism can come about later in the book.

---

## Part 2: Transport Mechanisms

### SSE vs STDIO

Starting from what MCP is and how it came to be, it would be good to talk about alternative systems. A couple of terms you'll come across: Server Sent Events (SSE) and STDIO - two mechanisms. This is moving so fast that I can never remember which is now mostly deprecated. SSE is the older one. So SSE is deprecated mostly; the direction is moving towards STDIO.

### Remote vs Local MCP

Either way, we have remote versus local MCP - that's a fundamental distinction. It would be good to talk about why sometimes you'll find the same service has both a remote and a local MCP. Why would people want to use a local MCP when they could use it remotely?

Some MCPs are local only for obvious reasons - like I just created an MCP for my NAS, which is a local MCP. But in other cases - probably most cases - it's not so clear cut why one would choose one over the other. Frequently they're offered in parallel, which adds to the confusion about MCP, of which there is a lot.

---

## Part 3: Security

### The Core Security Question

MCP is potentially a massive risk. Typically, authentication is handled at the API level - we understand that. But what happens when suddenly you've got a bunch of GitHub MCPs and you don't know which one is legit? Maybe that's a bad example since GitHub has an official MCP. But in other cases there are third-party ones, and you think: "Wait, if I'm putting my API key into connecting to this remote MCP, that sounds very risky."

MCP security is a key topic.

---

## Part 4: The MCP Ecosystem

### Registry Proliferation

Another concept that could be very useful to cover is the booming scene of MCP registries. Smithery has one, GitHub has one - everyone and their grandmother seems to be coming out with an MCP registry. This adds another layer of confusion for users trying to figure out which registry to use.

### Tool Fragmentation and Standardization

What you'll commonly see is that different tools all have their own MCP definitions. VS Code, Cline, Roo Code, Windsurf - they all want their own MCP file. I started using a good tool called MCPM - there's an MCP manager and a proxy. It's unfortunate that this is necessary.

This begs the question: why do we see so much splintering? Why are these different tools insisting on their own libraries, forcing developers to say "this is ridiculous" and create tools for a single management interface to proxy that? Why are these proprietary systems emerging for how developers define the MCP tools they use? Why haven't we seen standardization around central management - one definition on your computer where we expect to find it?

Standardization is really key here. I'd say it's a key point about the MCP picture.

### Personal Assessment

Thinking through my experience using MCP for a while: it's cumbersome, but once you get the hang of it, it's brilliant. I really think it's potentially fantastic - it is a fantastic technology, just mired in a lot of early-stage confusion.

---

## Part 5: Pros and Cons

### Benefits

The pros are quite straightforward, but maybe some less obvious ones too. Obvious ones: it's great that you can get your chatbot to send an email from your account. What else can we do?

A very interesting one in agentic AI is payments - giving agents wallets. What else can we give them through MCP? Where are the limits?

### The Limits of MCP

We would tend towards saying that MCP can allow agents to interact with everything with an API. Where does that stop? That's technical systems, but what are the edge cases - the boldest, far reaches of what MCP could really do?

If the nuclear codes had an API - crazy example - could it launch? Operational technology, OT, SCADA systems in offline environments - any potential there? I don't know why I thought of those, the most secure computing environments.

---

## Part 6: Vendors and the Emerging Landscape

### Industry Adoption

Let's talk about vendors and the emerging picture in MCP. Anthropic came up with it. I thought it was a pivotal moment when OpenAI said they're going to support MCP. I wouldn't say it was a concession - I thought it was actually a good thing that another major vendor and rival said "okay, this is a good thing, we're not going to come up with our own." OpenAI didn't come up with a "better MCP." This is a good point to discuss: are there any alternatives?

### The CLI Alternative Question

Here's one question I'd like to discuss somewhere in this text. Something I've done with my agents: take a CLI like `gh` for GitHub or Hugging Face. It's very well documented and is actually in the knowledge base for most agents or large language models. Before I figured out the basics of MCP, I would say in a system prompt "here's GH, use it to manage GitHub" - and it actually just worked.

That led me to ask: why don't we just provide a better way for AI tools to look up command line interfaces? That whole field is emerging with tools like Context7. For me, this begs the question: why don't we just do this? Instead of every single API coming up with its own MCP, why don't we have one API like Context7 that gathers together all the documentation, and then we won't need hundreds of MCPs in parallel to APIs?

That's a thoughtful question to be considered.

---

## Part 7: Enterprise and the Future of Work

### MCP Proxying and Gateways

At the more technical level, we'll talk about MCP proxying and MCP gateways, which are emerging and important.

### The "Connectors" Vision

I'm working on a project about the companies of tomorrow, where MCP has some name that people are familiar with. "Connectors" is kind of emerging as one. The company says "Welcome to Acme Limited. On your first day, Daniel, we're glad to connect you to..." - and instead of "here's your email account" or "here's our Slack," they'll say "here's our in-house AI tool, and this is your passkey to the MCP."

Everyone working in the knowledge economy has a parallel personal digital life and a work digital life. At home, I have my MCPs for Spotify or something, and I have my work MCPs.

### Remote Work and Federation

How will the average knowledge worker of tomorrow manage this? Besides people who work in very secure industries, most of us don't work in the government sector or have extraordinary security requirements. We're probably going to be working from home for the foreseeable future - not all the time, but some remote work will be going on. There'll be a need for remote workers to have access to their company's connectors or MCPs.

What are the best practices emerging in terms of federation? Right now I don't think it's really even a thing yet - MCP isn't developed enough. There's not even really a decent chatbot for the desktop besides Claude Code, I guess. There's barely one for Android. We're still at quite an early stage in overall development.

It won't be a challenge until we're further on and connectors become something people know about. Today I might say "I'm really interested in MCP" and get a blank look from everyone except folks interested in AI tech. But maybe in a year or five years, there might be a market for connectors - it might be mainstream.

When we get to that point of maturity, what would the system look like?

---

## Part 8: Global Perspectives

### East vs West in AI

One topic I find very interesting: East versus West in AI. I love to explore the Chinese models on Qwen for image generation, for generative AI. I love to see how they're doing things differently. It would be really interesting to talk about within MCP: what have been some of the most impressive use cases so far?

---

## Part 9: Custom MCP Development

### Tool Definition Challenges

I've been developing custom MCPs and finding it really useful. One challenge is tool definition - the more tools, the more context consumed.

I've read (I don't know if it's correct) that Anthropic is working on a way at the protocol level to make tool exposure very defined - so that instead of wrestling to turn tools on and off like a button, there's going to be a more sophisticated solution. If that's true, I'd love to learn more about that.

### The Reality of Custom Development

Coming back to custom MCPs - I think I would rather not have to create them, to be honest. I'd prefer that someone has created it and I can just get on to using it, because MCP is just a tool. People don't want to make tools or use tools so much as to do things with these technologies.

But of course there are going to be some MCPs - MCP as a layer over APIs. I've mostly worked in-house with small to medium companies, but I'm sure enterprises have internal APIs and proprietary systems. In those cases, they'd want to be creating their own proprietary MCPs. So there's that market for private, non-commercial MCPs.

---

## Part 10: Public Data and Open Government

### MCPs for Public APIs

While expanding on the curriculum, I've noticed that MCPs aren't always about authenticated APIs. I always assumed whenever I used an MCP, it was either a filesystem MCP or an authenticated API. Then I used a couple that were just MCPs over public APIs - no authentication needed, nice and easy to set up.

### Open Data Initiatives

This is really useful for large datasets. Think about UN data, World Bank data that is already public. This is a potential great use case. There are a lot of great open data initiatives in the world.

Frequently the problem is that organizations like the World Bank and OECD are releasing data - they're being transparent, they're putting it out there onto data portals. But even if they provide nice visualization and download tools, by itself it's almost not that helpful. There's just a mountain of information to wade through.

The idea that this could be exposed via conversational interfaces is really powerful. I'd be interested to know if governments are exploring how MCP could be used as part of transparency and open data initiatives - open government. If there's any movement there, I would love to include it in the curriculum.

---

## Curriculum Summary

### Core Topics

1. **What is MCP?** - Definition, origin story at Anthropic, the people behind it
2. **History** - One year since launch, development timeline
3. **Criticisms and Controversy** - "It's just an API wrapper" debate
4. **Transport Mechanisms** - SSE (deprecated) vs STDIO (current direction)
5. **Remote vs Local MCPs** - When to use each, why both exist, trade-offs

### Security and Trust

6. **Security Risks** - API key exposure, trusting third-party MCPs
7. **Authentication** - How MCP handles auth vs traditional API auth
8. **Verifying Legitimacy** - Official vs third-party MCPs

### Ecosystem and Fragmentation

9. **MCP Registries** - Smithery, GitHub, the proliferation problem
10. **Tool Fragmentation** - VS Code, Cline, Windsurf each wanting their own config
11. **MCPM and Proxy Tools** - Solutions for managing fragmentation
12. **Standardization** - Why it hasn't happened, what it would look like

### Use Cases and Limits

13. **Common Use Cases** - Email, file systems, API access
14. **Advanced Use Cases** - Payments, agent wallets
15. **Edge Cases** - OT/SCADA, secure environments, theoretical limits

### Industry Landscape

16. **Vendors** - Anthropic (creator), OpenAI adoption, ecosystem players
17. **CLI Alternative** - Using documented CLIs (gh, huggingface) vs MCPs
18. **Context7 Approach** - Centralized documentation vs per-API MCPs

### Enterprise and Future

19. **MCP Gateways/Proxies** - Enterprise architecture patterns
20. **"Connectors" Vision** - MCP in the workplace of tomorrow
21. **Personal vs Work MCPs** - Managing dual digital lives
22. **Federation** - Remote workers accessing company MCPs
23. **Maturity Timeline** - When will this go mainstream?

### Development

24. **Custom MCP Development** - When and why to build your own
25. **Tool Definition** - Context limits, Anthropic's work on better tool exposure
26. **Enterprise/Private MCPs** - Internal APIs, proprietary systems

### Global and Public Sector

27. **East vs West AI** - Chinese models (Qwen), different approaches
28. **Public API MCPs** - No-auth MCPs over public data
29. **Open Data** - UN, World Bank, OECD datasets via MCP
30. **Open Government** - MCP for transparency initiatives
