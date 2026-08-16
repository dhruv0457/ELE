"""LLM Clients - Unified Abstraction"""
import os
import json
import asyncio
from typing import AsyncGenerator, Optional, Dict, List, Any
from abc import ABC, abstractmethod
from dataclasses import dataclass

from app.config.settings import settings


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: Dict[str, int] = None


class LLMClient(ABC):
    """Abstract base class for LLM clients"""

    @abstractmethod
    async def complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: str = None,
        tools: List[Dict] = None,
    ) -> LLMResponse:
        pass

    @abstractmethod
    async def stream_complete(
        self,
        prompt: str,
        model: str,
        temperature: float = 0.7,
        max_tokens: int = 4096,
        system: str = None,
        tools: List[Dict] = None,
    ) -> AsyncGenerator[str, None]:
        pass


class OpenAIClient(LLMClient):
    def __init__(self, api_key: str):
        import openai
        self.client = openai.AsyncOpenAI(api_key=api_key)

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model,
            usage=response.usage.model_dump() if response.usage else None,
        )

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            tools=tools,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class GeminiClient(LLMClient):
    def __init__(self, api_key: str):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.genai = genai

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        gm = self.genai.GenerativeModel(model)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = await gm.generate_content_async(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
        )
        return LLMResponse(
            content=response.text or "",
            model=model,
        )

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        gm = self.genai.GenerativeModel(model)
        full_prompt = f"{system}\n\n{prompt}" if system else prompt
        response = await gm.generate_content_async(
            full_prompt,
            generation_config={
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            },
            stream=True,
        )
        async for chunk in response:
            if chunk.text:
                yield chunk.text


class GroqClient(LLMClient):
    def __init__(self, api_key: str):
        import groq
        self.client = groq.AsyncGroq(api_key=api_key)

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model,
        )

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class NVIDIAClient(LLMClient):
    def __init__(self, api_key: str):
        import openai
        self.client = openai.AsyncOpenAI(
            api_key=api_key,
            base_url="https://integrate.api.nvidia.com/v1",
        )

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        response = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.choices[0].message.content or "",
            model=model,
        )

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        stream = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content


class AnthropicClient(LLMClient):
    def __init__(self, api_key: str):
        import anthropic
        self.client = anthropic.AsyncAnthropic(api_key=api_key)

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        messages = [{"role": "user", "content": prompt}]
        response = await self.client.messages.create(
            model=model,
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return LLMResponse(
            content=response.content[0].text if response.content else "",
            model=model,
        )

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        messages = [{"role": "user", "content": prompt}]
        stream = await self.client.messages.create(
            model=model,
            messages=messages,
            system=system,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        async for chunk in stream:
            if chunk.type == "content_block_delta":
                yield chunk.delta.text


class OllamaClient(LLMClient):
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self._session = None

    def _get_session(self):
        """Lazily create aiohttp session"""
        import aiohttp
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
        return self._session

    async def complete(self, prompt, model, temperature, max_tokens, system, tools) -> LLMResponse:
        session = self._get_session()
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": False,
        }
        async with session.post(f"{self.base_url}/api/generate", json=payload) as resp:
            data = await resp.json()
            return LLMResponse(content=data.get("response", ""), model=model)

    async def stream_complete(self, prompt, model, temperature, max_tokens, system, tools):
        session = self._get_session()
        payload = {
            "model": model,
            "prompt": prompt,
            "system": system,
            "temperature": temperature,
            "num_predict": max_tokens,
            "stream": True,
        }
        async with session.post(f"{self.base_url}/api/generate", json=payload) as resp:
            async for line in resp.content:
                if line:
                    try:
                        data = json.loads(line)
                        if "response" in data:
                            yield data["response"]
                    except:
                        pass


class LLMOrchestrator:
    """Orchestrates multiple LLM providers"""

    def __init__(self):
        self.clients: Dict[str, LLMClient] = {}
        self._init_clients()

    def _init_clients(self):
        # Initialize clients based on available API keys
        if settings.OPENAI_API_KEY:
            self.clients["openai"] = OpenAIClient(settings.OPENAI_API_KEY)
        if settings.GEMINI_API_KEY:
            self.clients["gemini"] = GeminiClient(settings.GEMINI_API_KEY)
        if settings.GROQ_API_KEY:
            self.clients["groq"] = GroqClient(settings.GROQ_API_KEY)
        if settings.NVIDIA_API_KEY:
            self.clients["nvidia"] = NVIDIAClient(settings.NVIDIA_API_KEY)
        if settings.ANTHROPIC_API_KEY:
            self.clients["claude"] = AnthropicClient(settings.ANTHROPIC_API_KEY)
        # Ollama always available locally
        self.clients["ollama"] = OllamaClient()

    async def stream_parallel(
        self,
        messages: List[Dict],
        providers: List[str],
        tools: List[Dict] = None,
    ) -> AsyncGenerator[tuple[str, str], None]:
        """Stream from multiple providers in parallel"""
        # Get the last user message as prompt
        prompt = messages[-1]["content"] if messages else ""
        system = messages[0]["content"] if messages and messages[0]["role"] == "system" else None

        # Create tasks for each provider
        async def stream_provider(provider_name: str):
            client = self.clients.get(provider_name)
            if not client:
                return
            try:
                async for chunk in client.stream_complete(
                    prompt=prompt,
                    model=self._get_model_for_provider(provider_name),
                    temperature=0.7,
                    max_tokens=4096,
                    system=system,
                    tools=tools,
                ):
                    yield (provider_name, chunk)
            except Exception as e:
                yield (provider_name, f"[Error: {str(e)}]")

        # Run all providers concurrently
        tasks = [stream_provider(p) for p in providers]
        for task in asyncio.as_completed(tasks):
            async for item in task:
                yield item

    def _get_model_for_provider(self, provider: str) -> str:
        config = settings.get_llm_provider_config(provider)
        return config.model if config else provider

    async def merge_responses(self, responses: Dict[str, str]) -> str:
        """Heuristic merge: pick longest/best response"""
        if not responses:
            return ""
        # Simple heuristic: longest response
        return max(responses.values(), key=len)


# Global orchestrator (lazy singleton)
_orchestrator = None

def get_orchestrator() -> LLMOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = LLMOrchestrator()
    return _orchestrator

# Backward compatibility
orchestrator = get_orchestrator()