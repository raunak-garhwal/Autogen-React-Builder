from autogen import AssistantAgent, UserProxyAgent
from typing import Dict
import os

class StateMotionAgent:
    def __init__(self, config_list):
        self.config_list = config_list
        self.assistant = AssistantAgent(
            name="state_motion_builder",
            system_message="""You are a React state management and animation expert.
            Your role is to implement state management solutions and create smooth animations.""",
            llm_config={
                "config_list": config_list,
                "temperature": 0.7
            }
        )
        
        self.user_proxy = UserProxyAgent(
            name="state_motion_manager",
            code_execution_config={
                "work_dir": "generated",
                "use_docker": False
            },
            human_input_mode="NEVER"
        )

    async def setup_state_management(self, project_config: Dict, project_id: str) -> bool:
        """Set up state management and animations based on project configuration."""
        try:
            # Convert Pydantic model to dict if needed
            config_dict = project_config if isinstance(project_config, dict) else project_config.dict()
            
            project_dir = os.path.join("generated", project_id)
            
            # Setup state management if specified
            if config_dict["state_management"]:
                await self._setup_state_solution(project_dir, config_dict["state_management"])
            
            # Setup animations if enabled
            if config_dict["animations"]:
                await self._setup_animations(project_dir)
            
            return True
        except Exception as e:
            print(f"Error setting up state management: {str(e)}")
            return False

    async def _setup_state_solution(self, project_dir: str, state_management: str) -> None:
        """Set up the specified state management solution."""
        if state_management == "zustand":
            # Setup Zustand store
            store_dir = os.path.join(project_dir, "src", "store")
            os.makedirs(store_dir, exist_ok=True)
            # Implementation details for Zustand setup
            pass
        # Add other state management solutions as needed

    async def _setup_animations(self, project_dir: str) -> None:
        """Set up animation utilities and components."""
        # Implementation details for animation setup
        pass

    def _generate_app_store(self) -> str:
        """Generate the main app store using Zustand."""
        return """import { create } from 'zustand';

interface AppState {
  isLoading: boolean;
  error: string | null;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAppStore = create<AppState>((set) => ({
  isLoading: false,
  error: null,
  setLoading: (loading) => set({ isLoading: loading }),
  setError: (error) => set({ error })
}));"""

    def _generate_auth_store(self) -> str:
        """Generate the authentication store using Zustand."""
        return """import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface User {
  id: string;
  email: string;
  name: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  setUser: (user: User | null) => void;
  setToken: (token: string | null) => void;
  logout: () => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      token: null,
      setUser: (user) => set({ user }),
      setToken: (token) => set({ token }),
      logout: () => set({ user: null, token: null })
    }),
    {
      name: 'auth-storage'
    }
  )
);"""

    def _generate_theme_store(self) -> str:
        """Generate the theme store using Zustand."""
        return """import { create } from 'zustand';
import { persist } from 'zustand/middleware';

type Theme = 'light' | 'dark' | 'system';

interface ThemeState {
  theme: Theme;
  setTheme: (theme: Theme) => void;
}

export const useThemeStore = create<ThemeState>()(
  persist(
    (set) => ({
      theme: 'system',
      setTheme: (theme) => set({ theme })
    }),
    {
      name: 'theme-storage'
    }
  )
);"""

    def _generate_transitions(self) -> str:
        """Generate common transition configurations."""
        return """export const transitions = {
  ease: {
    default: [0.4, 0, 0.2, 1],
    in: [0.4, 0, 1, 1],
    out: [0, 0, 0.2, 1],
    inOut: [0.4, 0, 0.2, 1]
  },
  duration: {
    shortest: 0.15,
    shorter: 0.2,
    short: 0.25,
    standard: 0.3,
    complex: 0.375,
    enteringScreen: 0.225,
    leavingScreen: 0.195
  }
};

export const spring = {
  gentle: {
    type: "spring",
    damping: 15,
    stiffness: 100
  },
  bouncy: {
    type: "spring",
    damping: 10,
    stiffness: 100
  },
  slow: {
    type: "spring",
    damping: 20,
    stiffness: 50
  }
} as const;"""

    def _generate_variants(self) -> str:
        """Generate common animation variants."""
        return """import { Variants } from 'framer-motion';

export const fadeIn: Variants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3
    }
  }
};

export const slideUp: Variants = {
  hidden: {
    opacity: 0,
    y: 20
  },
  visible: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.3
    }
  }
};

export const slideIn: Variants = {
  hidden: {
    opacity: 0,
    x: -20
  },
  visible: {
    opacity: 1,
    x: 0,
    transition: {
      duration: 0.3
    }
  }
};

export const staggerChildren: Variants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.1
    }
  }
};"""

    def _generate_animation_hooks(self) -> str:
        """Generate custom animation hooks."""
        return """import { useEffect } from 'react';
import { useAnimation, AnimationControls } from 'framer-motion';
import { useInView } from 'react-intersection-observer';

export function useScrollAnimation(): [boolean, AnimationControls] {
  const controls = useAnimation();
  const [ref, inView] = useInView({
    threshold: 0.1,
    triggerOnce: true
  });

  useEffect(() => {
    if (inView) {
      controls.start('visible');
    }
  }, [controls, inView]);

  return [inView, controls];
}

export function useAnimateOnMount(delay: number = 0) {
  const controls = useAnimation();

  useEffect(() => {
    controls.start('visible');
  }, [controls]);

  return {
    initial: 'hidden',
    animate: controls,
    variants: {
      hidden: { opacity: 0, y: 20 },
      visible: {
        opacity: 1,
        y: 0,
        transition: {
          duration: 0.6,
          delay
        }
      }
    }
  };
}""" 