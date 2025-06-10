from autogen import AssistantAgent, UserProxyAgent
from typing import Dict
import os

class DevToolsAgent:
    def __init__(self, config_list):
        self.config_list = config_list
        self.assistant = AssistantAgent(
            name="dev_tools_builder",
            system_message="""You are a React development tools expert.
            Your role is to set up and configure development tools, testing frameworks,
            and debugging utilities for React applications.""",
            llm_config={
                "config_list": config_list,
                "temperature": 0.7
            }
        )
        
        self.user_proxy = UserProxyAgent(
            name="dev_tools_manager",
            code_execution_config={
                "work_dir": "generated",
                "use_docker": False
            },
            human_input_mode="NEVER"
        )

    async def setup_dev_tools(self, project_config: Dict, project_id: str) -> bool:
        """Set up development tools if enabled."""
        if not project_config.get("dev_tools"):
            return True
            
        try:
            project_dir = os.path.join("generated", project_id)
            
            # Set up Monaco Editor
            await self._setup_monaco_editor(project_dir)
            
            # Set up testing environment
            await self._setup_testing(project_dir)
            
            # Set up development utilities
            await self._setup_utilities(project_dir)
            
            return True
        except Exception as e:
            print(f"Error setting up dev tools: {str(e)}")
            return False

    async def _setup_monaco_editor(self, project_dir: str):
        """Set up Monaco Editor integration."""
        # Create components directory
        editor_dir = os.path.join(project_dir, "src/components/editor")
        os.makedirs(editor_dir, exist_ok=True)
        
        # Generate editor components
        components = {
            "CodeEditor.tsx": self._generate_code_editor(),
            "useMonaco.ts": self._generate_monaco_hook(),
            "theme.ts": self._generate_editor_theme()
        }
        
        for filename, content in components.items():
            with open(os.path.join(editor_dir, filename), "w") as f:
                f.write(content)

    async def _setup_testing(self, project_dir: str):
        """Set up testing environment with Vitest and Testing Library."""
        # Update package.json with testing dependencies
        package_path = os.path.join(project_dir, "package.json")
        with open(package_path, "r") as f:
            package = eval(f.read())
            
        package["scripts"]["test"] = "vitest"
        package["scripts"]["test:ui"] = "vitest --ui"
        package["scripts"]["coverage"] = "vitest run --coverage"
        
        package["devDependencies"].update({
            "@testing-library/react": "^14.0.0",
            "@testing-library/user-event": "^14.4.3",
            "@vitest/coverage-v8": "^0.34.4",
            "@vitest/ui": "^0.34.4",
            "jsdom": "^22.1.0",
            "vitest": "^0.34.4"
        })
        
        with open(package_path, "w") as f:
            f.write(str(package))
            
        # Create test setup files
        setup_dir = os.path.join(project_dir, "src/test")
        os.makedirs(setup_dir, exist_ok=True)
        
        with open(os.path.join(setup_dir, "setup.ts"), "w") as f:
            f.write(self._generate_test_setup())

    async def _setup_utilities(self, project_dir: str):
        """Set up development utilities."""
        utils_dir = os.path.join(project_dir, "src/utils")
        
        # Generate utility files
        utils = {
            "logger.ts": self._generate_logger(),
            "performance.ts": self._generate_performance_utils(),
            "debug.ts": self._generate_debug_utils()
        }
        
        for filename, content in utils.items():
            with open(os.path.join(utils_dir, filename), "w") as f:
                f.write(content)

    def _generate_code_editor(self) -> str:
        """Generate Monaco Editor component."""
        return """import { useEffect, useRef } from 'react';
import * as monaco from 'monaco-editor';
import { useMonaco } from './useMonaco';
import { editorTheme } from './theme';

interface CodeEditorProps {
  value: string;
  language?: string;
  onChange?: (value: string) => void;
  readOnly?: boolean;
}

export default function CodeEditor({
  value,
  language = 'typescript',
  onChange,
  readOnly = false
}: CodeEditorProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const { initializeMonaco } = useMonaco();
  
  useEffect(() => {
    if (!editorRef.current) return;
    
    initializeMonaco();
    
    const editor = monaco.editor.create(editorRef.current, {
      value,
      language,
      theme: 'customTheme',
      minimap: { enabled: false },
      fontSize: 14,
      lineNumbers: 'on',
      readOnly,
      automaticLayout: true,
      scrollBeyondLastLine: false
    });
    
    if (onChange) {
      editor.onDidChangeModelContent(() => {
        onChange(editor.getValue());
      });
    }
    
    return () => {
      editor.dispose();
    };
  }, [value, language, onChange, readOnly, initializeMonaco]);
  
  return (
    <div
      ref={editorRef}
      className="w-full h-[500px] border border-gray-200 rounded-md overflow-hidden"
    />
  );
}"""

    def _generate_monaco_hook(self) -> str:
        """Generate Monaco Editor hook."""
        return """import { useCallback } from 'react';
import * as monaco from 'monaco-editor';
import { editorTheme } from './theme';

export function useMonaco() {
  const initializeMonaco = useCallback(() => {
    monaco.editor.defineTheme('customTheme', editorTheme);
    monaco.editor.setTheme('customTheme');
    
    // Configure TypeScript
    monaco.languages.typescript.typescriptDefaults.setCompilerOptions({
      target: monaco.languages.typescript.ScriptTarget.ESNext,
      allowNonTsExtensions: true,
      moduleResolution: monaco.languages.typescript.ModuleResolutionKind.NodeJs,
      module: monaco.languages.typescript.ModuleKind.ESNext,
      noEmit: true,
      esModuleInterop: true,
      jsx: monaco.languages.typescript.JsxEmit.React,
      reactNamespace: 'React',
      allowJs: true,
      typeRoots: ['node_modules/@types']
    });
    
    // Add React types
    fetch('https://unpkg.com/@types/react@latest/index.d.ts').then(async (response) => {
      const reactTypes = await response.text();
      monaco.languages.typescript.typescriptDefaults.addExtraLib(
        reactTypes,
        'file:///node_modules/@types/react/index.d.ts'
      );
    });
  }, []);
  
  return { initializeMonaco };
}"""

    def _generate_editor_theme(self) -> str:
        """Generate Monaco Editor theme."""
        return """import { editor } from 'monaco-editor';

export const editorTheme: editor.IStandaloneThemeData = {
  base: 'vs-dark',
  inherit: true,
  rules: [
    { token: 'comment', foreground: '6A9955' },
    { token: 'keyword', foreground: 'C586C0' },
    { token: 'string', foreground: 'CE9178' },
    { token: 'number', foreground: 'B5CEA8' },
    { token: 'regexp', foreground: 'D16969' },
    { token: 'type', foreground: '4EC9B0' },
    { token: 'class', foreground: '4EC9B0' },
    { token: 'function', foreground: 'DCDCAA' },
    { token: 'variable', foreground: '9CDCFE' },
    { token: 'constant', foreground: '4FC1FF' }
  ],
  colors: {
    'editor.background': '#1E1E1E',
    'editor.foreground': '#D4D4D4',
    'editor.lineHighlightBackground': '#2F2F2F',
    'editor.selectionBackground': '#264F78',
    'editor.inactiveSelectionBackground': '#3A3D41'
  }
};"""

    def _generate_test_setup(self) -> str:
        """Generate test setup configuration."""
        return """import { expect, afterEach } from 'vitest';
import { cleanup } from '@testing-library/react';
import matchers from '@testing-library/jest-dom/matchers';

// Extend Vitest's expect method with Testing Library matchers
expect.extend(matchers);

// Cleanup after each test
afterEach(() => {
  cleanup();
});"""

    def _generate_logger(self) -> str:
        """Generate logger utility."""
        return """type LogLevel = 'debug' | 'info' | 'warn' | 'error';

interface LogOptions {
  level?: LogLevel;
  context?: string;
  data?: unknown;
}

class Logger {
  private isDevelopment = process.env.NODE_ENV === 'development';

  debug(message: string, options: Omit<LogOptions, 'level'> = {}) {
    this.log(message, { ...options, level: 'debug' });
  }

  info(message: string, options: Omit<LogOptions, 'level'> = {}) {
    this.log(message, { ...options, level: 'info' });
  }

  warn(message: string, options: Omit<LogOptions, 'level'> = {}) {
    this.log(message, { ...options, level: 'warn' });
  }

  error(message: string, options: Omit<LogOptions, 'level'> = {}) {
    this.log(message, { ...options, level: 'error' });
  }

  private log(message: string, { level = 'info', context, data }: LogOptions = {}) {
    if (!this.isDevelopment && level === 'debug') return;

    const timestamp = new Date().toISOString();
    const contextString = context ? `[${context}]` : '';
    const logMessage = `${timestamp} ${level.toUpperCase()} ${contextString} ${message}`;

    switch (level) {
      case 'debug':
        console.debug(logMessage, data || '');
        break;
      case 'info':
        console.info(logMessage, data || '');
        break;
      case 'warn':
        console.warn(logMessage, data || '');
        break;
      case 'error':
        console.error(logMessage, data || '');
        break;
    }
  }
}

export const logger = new Logger();"""

    def _generate_performance_utils(self) -> str:
        """Generate performance utility functions."""
        return """export function measureExecutionTime<T>(
  fn: () => T,
  context?: string
): T {
  const start = performance.now();
  const result = fn();
  const end = performance.now();
  
  console.debug(
    `[Performance]${context ? ` ${context}:` : ''} ${(end - start).toFixed(2)}ms`
  );
  
  return result;
}

export async function measureAsyncExecutionTime<T>(
  fn: () => Promise<T>,
  context?: string
): Promise<T> {
  const start = performance.now();
  const result = await fn();
  const end = performance.now();
  
  console.debug(
    `[Performance]${context ? ` ${context}:` : ''} ${(end - start).toFixed(2)}ms`
  );
  
  return result;
}

export function createDebounce(delay: number) {
  let timeoutId: NodeJS.Timeout;
  
  return (fn: () => void) => {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(fn, delay);
  };
}

export function createThrottle(delay: number) {
  let lastRun = 0;
  let timeoutId: NodeJS.Timeout;
  
  return (fn: () => void) => {
    const now = Date.now();
    
    if (lastRun + delay < now) {
      fn();
      lastRun = now;
    } else {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(fn, delay);
    }
  };
}"""

    def _generate_debug_utils(self) -> str:
        """Generate debugging utility functions."""
        return """interface DebugConfig {
  enabled: boolean;
  level: 'verbose' | 'normal' | 'minimal';
}

let debugConfig: DebugConfig = {
  enabled: process.env.NODE_ENV === 'development',
  level: 'normal'
};

export function configureDebug(config: Partial<DebugConfig>) {
  debugConfig = { ...debugConfig, ...config };
}

export function debug(message: string, data?: unknown) {
  if (!debugConfig.enabled) return;
  
  const timestamp = new Date().toISOString();
  console.debug(`[${timestamp}] ${message}`, data || '');
}

export function debugVerbose(message: string, data?: unknown) {
  if (!debugConfig.enabled || debugConfig.level !== 'verbose') return;
  
  const timestamp = new Date().toISOString();
  console.debug(`[VERBOSE][${timestamp}] ${message}`, data || '');
}

export function debugComponent(componentName: string) {
  if (!debugConfig.enabled) return {};
  
  return {
    debug: (message: string, data?: unknown) => {
      debug(`[${componentName}] ${message}`, data);
    },
    logProps: (props: Record<string, unknown>) => {
      debug(`[${componentName}] Props:`, props);
    },
    logState: (state: Record<string, unknown>) => {
      debug(`[${componentName}] State:`, state);
    },
    logEffect: (effectName: string) => {
      debug(`[${componentName}] Effect: ${effectName}`);
    }
  };
}""" 