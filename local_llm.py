#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
本地LLM推理（无需API）
基于 llama-cpp-python，加载本地GGUF模型进行推理。

使用方式：
from local_llm import ensure_loaded, generate_reply
ensure_loaded(model_path="./models/llm/model.gguf")
text = generate_reply("你好")
"""

import os
import sys
import threading
import contextlib
from typing import Optional

_llama = None
_lock = threading.Lock()


@contextlib.contextmanager
def _suppress_stdout_stderr():
    """静默第三方底层初始化输出（如ggml/metal）。"""
    old_out, old_err = sys.stdout, sys.stderr
    try:
        with open(os.devnull, "w") as devnull_out, open(os.devnull, "w") as devnull_err:
            sys.stdout, sys.stderr = devnull_out, devnull_err
            yield
    finally:
        sys.stdout, sys.stderr = old_out, old_err


def ensure_loaded(
    model_path: str = "./models/llm/model.gguf",
    n_ctx: int = 8192,
    n_threads: Optional[int] = None,
    n_gpu_layers: int = 20,
) -> bool:
    """懒加载本地模型。返回是否加载成功。"""
    global _llama
    if _llama is not None:
        return True
    if not os.path.exists(model_path):
        return False
    with _lock:
        if _llama is not None:
            return True
        try:
            # 延迟导入，避免环境未装包时报错影响主流程
            from llama_cpp import Llama
            _threads = n_threads or os.cpu_count() or 4
            _gpu_layers = max(0, int(n_gpu_layers))
            _ctx = max(1024, int(n_ctx))
            with _suppress_stdout_stderr():
                _llocal = Llama(
                    model_path=model_path,
                    n_ctx=_ctx,
                    n_threads=_threads,
                    n_gpu_layers=_gpu_layers,
                    embedding=False,
                    verbose=False,
                )
            _llama = _llocal
            return True
        except Exception:
            return False


def generate_reply(user_text: str, max_tokens: int = 256, temperature: float = 0.7) -> Optional[str]:
    """使用已加载的本地模型生成回复。若模型未加载或失败，返回None。"""
    global _llama
    if _llama is None:
        return None
    
    try:
        with _suppress_stdout_stderr():
            # 使用chat completion格式，更适合Qwen2.5模型
            response = _llama.create_chat_completion(
                messages=[{"role": "user", "content": user_text}],
                max_tokens=max_tokens,
                temperature=temperature,
                top_p=0.9,
                repeat_penalty=1.1,
                stop=["<|im_end|>", "Human:", "User:", "\n\nUser:"]
            )
        text = response["choices"][0]["message"]["content"].strip()
        return text or None
    except Exception as e:
        print(f"LLM生成失败: {e}")
        return None


