from autogen import AssistantAgent, UserProxyAgent
from typing import Dict, List
import os
import json

class InterfaceAgent:
    def __init__(self, config_list):
        self.config_list = config_list
        self.assistant = AssistantAgent(
            name="interface_builder",
            system_message="""You are a React UI/UX expert.
            Your role is to create modern, accessible, and responsive React components
            following best practices and design patterns.""",
            llm_config={
                "config_list": config_list,
                "temperature": 0.7
            }
        )
        
        self.user_proxy = UserProxyAgent(
            name="interface_manager",
            code_execution_config={
                "work_dir": "generated",
                "use_docker": False
            },
            human_input_mode="NEVER"
        )

    async def generate_components(self, project_config: Dict, project_id: str) -> bool:
        """Generate React components based on project configuration."""
        try:
            # Convert Pydantic model to dict if needed
            config_dict = project_config.dict() if hasattr(project_config, 'dict') else project_config
            
            project_dir = os.path.join("generated", project_id)
            
            # Create src and components directories
            os.makedirs(os.path.join(project_dir, "src", "components"), exist_ok=True)
            
            # Generate base components
            await self._create_layout_components(project_dir, config_dict)
            await self._create_common_components(project_dir, config_dict)
            
            # Generate feature-specific components if features are specified
            features = config_dict.get("features", [])
            if features:
                await self._create_feature_components(project_dir, features)
            
            # Generate pages if routing is enabled
            if config_dict.get("routing"):
                await self._create_pages(project_dir, config_dict)
            
            return True
        except Exception as e:
            print(f"Error generating components: {str(e)}")
            return False

    async def _create_layout_components(self, project_dir: str, config: Dict):
        """Create layout components like Header, Footer, Layout."""
        try:
            components = {
                "Layout.jsx": self._generate_layout_component(config),
                "Header.jsx": self._generate_header_component(config),
                "Footer.jsx": self._generate_footer_component(config)
            }
            
            layout_dir = os.path.join(project_dir, "src", "components", "layout")
            os.makedirs(layout_dir, exist_ok=True)
            
            for filename, content in components.items():
                filepath = os.path.join(layout_dir, filename)
                with open(filepath, "w") as f:
                    f.write(content)
        except Exception as e:
            print(f"Error creating layout components: {str(e)}")
            raise

    async def _create_common_components(self, project_dir: str, config: Dict):
        """Create common UI components based on configuration."""
        try:
            components = {
                "Button.jsx": self._generate_button_component(config),
                "Card.jsx": self._generate_card_component(config),
                "Input.jsx": self._generate_input_component(config)
            }
            
            ui_dir = os.path.join(project_dir, "src", "components", "ui")
            os.makedirs(ui_dir, exist_ok=True)
            
            for filename, content in components.items():
                filepath = os.path.join(ui_dir, filename)
                with open(filepath, "w") as f:
                    f.write(content)
        except Exception as e:
            print(f"Error creating common components: {str(e)}")
            raise

    async def _create_feature_components(self, project_dir: str, features: List[str]):
        """Create components for specific features."""
        try:
            features_dir = os.path.join(project_dir, "src", "components", "features")
            os.makedirs(features_dir, exist_ok=True)
            
            for feature in features:
                feature_dir = os.path.join(features_dir, feature.lower())
                os.makedirs(feature_dir, exist_ok=True)
                
                # Generate feature-specific components
                components = self._generate_feature_specific_components(feature)
                
                for filename, content in components.items():
                    filepath = os.path.join(feature_dir, filename)
                    with open(filepath, "w") as f:
                        f.write(content)
        except Exception as e:
            print(f"Error creating feature components: {str(e)}")
            raise

    def _generate_feature_specific_components(self, feature: str) -> Dict[str, str]:
        """Generate components specific to a feature."""
        components = {}
        
        # Convert feature name to proper case and create index file
        feature_name = "".join(word.capitalize() for word in feature.split("_"))
        
        # Create index file
        components["index.js"] = f"export * from './{feature_name}';\n"
        
        # Create main feature component
        components[f"{feature_name}.jsx"] = (
            f"import React from 'react';\n\n"
            f"const {feature_name} = (props) => {{\n"
            f"  return (\n"
            f"    <div className=\"p-4\">\n"
            f"      <h2 className=\"text-2xl font-bold mb-4\">{feature_name}</h2>\n"
            f"      {{/* Add your component content here */}}\n"
            f"    </div>\n"
            f"  );\n"
            f"}};\n\n"
            f"export default {feature_name};"
        )
        
        return components

    async def _create_pages(self, project_dir: str, config: Dict):
        """Create page components if routing is enabled."""
        try:
            pages_dir = os.path.join(project_dir, "src", "pages")
            os.makedirs(pages_dir, exist_ok=True)
            
            pages = {
                "Home.jsx": self._generate_home_page(config),
                "About.jsx": self._generate_about_page(config),
                "NotFound.jsx": self._generate_not_found_page(config)
            }
            
            for filename, content in pages.items():
                filepath = os.path.join(pages_dir, filename)
                with open(filepath, "w") as f:
                    f.write(content)
        except Exception as e:
            print(f"Error creating pages: {str(e)}")
            raise

    def _generate_layout_component(self, config: Dict) -> str:
        """Generate the main Layout component."""
        return """import { ReactNode } from 'react';
import Header from './Header';
import Footer from './Footer';

export default function Layout({ children }) {
  return (
    <div className="min-h-screen flex flex-col">
      <Header />
      <main className="flex-grow container mx-auto px-4 py-8">
        {children}
      </main>
      <Footer />
    </div>
  );
}"""

    def _generate_header_component(self, config: Dict) -> str:
        """Generate the Header component."""
        return """import { Link } from 'react-router-dom';

export default function Header() {
  return (
    <header className="bg-white shadow-sm">
      <nav className="container mx-auto px-4 py-4">
        <div className="flex justify-between items-center">
          <Link to="/" className="text-xl font-bold">
            {config['project_name']}
          </Link>
          <div className="space-x-4">
            <Link to="/" className="hover:text-gray-600">Home</Link>
            <Link to="/about" className="hover:text-gray-600">About</Link>
          </div>
        </div>
      </nav>
    </header>
  );
}"""

    def _generate_footer_component(self, config: Dict) -> str:
        """Generate the Footer component."""
        return """export default function Footer() {
  return (
    <footer className="bg-gray-50 border-t">
      <div className="container mx-auto px-4 py-6">
        <p className="text-center text-gray-600">
          © {new Date().getFullYear()} {config['project_name']}. All rights reserved.
        </p>
      </div>
    </footer>
  );
}"""

    def _generate_button_component(self, config: Dict) -> str:
        """Generate a reusable Button component."""
        return """import React from 'react';

const Button = ({ 
    children, 
    className = '', 
    variant = 'primary', 
    size = 'md', 
    ...props 
}) => {
    const baseStyles = 'inline-flex items-center justify-center rounded-md font-medium transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2';
    const variants = {
        primary: 'bg-blue-600 text-white hover:bg-blue-700',
        secondary: 'bg-gray-600 text-white hover:bg-gray-700',
        outline: 'border-2 border-gray-300 hover:bg-gray-50'
    };
    const sizes = {
        sm: 'px-3 py-1.5 text-sm',
        md: 'px-4 py-2 text-base',
        lg: 'px-6 py-3 text-lg'
    };
    
    return (
        <button
            className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
            {...props}
        >
            {children}
        </button>
    );
};

export default Button;"""

    def _generate_card_component(self, config: Dict) -> str:
        """Generate a reusable Card component."""
        return """import React from 'react';

const Card = ({ children, className = '' }) => {
    return (
        <div className={`bg-white rounded-lg shadow-md p-6 ${className}`}>
            {children}
        </div>
    );
};

export default Card;"""

    def _generate_input_component(self, config: Dict) -> str:
        """Generate a reusable Input component."""
        return """import React from 'react';

const Input = ({ 
    className = '', 
    label, 
    error, 
    ...props 
}) => {
    return (
        <div className="space-y-2">
            {label && (
                <label className="block text-sm font-medium text-gray-700">
                    {label}
                </label>
            )}
            <input
                className={`block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm ${className}`}
                {...props}
            />
            {error && (
                <p className="text-sm text-red-600">{error}</p>
            )}
        </div>
    );
};

export default Input;"""

    def _generate_home_page(self, config: Dict) -> str:
        """Generate the Home page component."""
        return """import React from 'react';
import { motion } from 'framer-motion';
import Card from '../components/Card';
import Button from '../components/Button';

const Home = () => {
    return (
        <div className="space-y-8">
            <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5 }}
            >
                <h1 className="text-4xl font-bold">Welcome to {config['project_name']}</h1>
                <p className="mt-4 text-lg text-gray-600">
                    {config.get('description', 'A modern React application')}
                </p>
            </motion.div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <Card>
                    <h2 className="text-xl font-semibold mb-4">Feature 1</h2>
                    <p className="text-gray-600">Description of feature 1</p>
                    <Button className="mt-4">Learn More</Button>
                </Card>
                
                <Card>
                    <h2 className="text-xl font-semibold mb-4">Feature 2</h2>
                    <p className="text-gray-600">Description of feature 2</p>
                    <Button variant="secondary" className="mt-4">Learn More</Button>
                </Card>
                
                <Card>
                    <h2 className="text-xl font-semibold mb-4">Feature 3</h2>
                    <p className="text-gray-600">Description of feature 3</p>
                    <Button variant="outline" className="mt-4">Learn More</Button>
                </Card>
            </div>
        </div>
    );
};

export default Home;"""

    def _generate_about_page(self, config: Dict) -> str:
        """Generate the About page component."""
        return """import { motion } from 'framer-motion';

export default function About() {
  return (
    <motion.div
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
      className="max-w-3xl mx-auto"
    >
      <h1 className="text-4xl font-bold mb-6">About Us</h1>
      <div className="prose prose-lg">
        <p>
          Welcome to {config['project_name']}. We are dedicated to providing
          the best experience for our users.
        </p>
        <h2>Our Mission</h2>
        <p>
          Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do
          eiusmod tempor incididunt ut labore et dolore magna aliqua.
        </p>
        <h2>Contact Us</h2>
        <p>
          Have questions? Feel free to reach out to us at{' '}
          <a href="mailto:contact@example.com">contact@example.com</a>
        </p>
      </div>
    </motion.div>
  );
}"""

    def _generate_not_found_page(self, config: Dict) -> str:
        """Generate the 404 Not Found page component."""
        return """import { Link } from 'react-router-dom';
import Button from '@/components/ui/Button';

export default function NotFound() {
  return (
    <div className="min-h-[50vh] flex flex-col items-center justify-center text-center">
      <h1 className="text-6xl font-bold text-gray-900">404</h1>
      <p className="mt-4 text-xl text-gray-600">Page not found</p>
      <p className="mt-2 text-gray-500">
        The page you're looking for doesn't exist or has been moved.
      </p>
      <Link to="/">
        <Button className="mt-8">
          Return Home
        </Button>
      </Link>
    </div>
  );
}""" 