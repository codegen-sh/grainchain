import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'GrainChain Documentation',
  description: 'Langchain for sandboxes - A powerful framework for building sandbox-aware AI applications',
  
  // GitHub Pages deployment configuration
  base: '/grainchain/',
  
  themeConfig: {
    // Navigation
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Guide', link: '/guide/' },
      { text: 'API', link: '/api/' },
      { text: 'CLI', link: '/cli/' },
      { text: 'Examples', link: '/examples/' },
      { text: 'Developer', link: '/developer/' }
    ],

    // Sidebar
    sidebar: {
      '/guide/': [
        {
          text: 'Getting Started',
          items: [
            { text: 'Introduction', link: '/guide/' },
            { text: 'Quick Start', link: '/guide/quick-start' },
            { text: 'Installation', link: '/guide/installation' },
            { text: 'Configuration', link: '/guide/configuration' }
          ]
        },
        {
          text: 'Core Concepts',
          items: [
            { text: 'Design Overview', link: '/guide/design' },
            { text: 'Sandbox Integration', link: '/guide/sandbox-integration' },
            { text: 'Docker Setup', link: '/guide/docker-setup' },
            { text: 'Analysis Guide', link: '/guide/analysis' }
          ]
        },
        {
          text: 'Advanced Topics',
          items: [
            { text: 'Benchmarking', link: '/guide/benchmarking' },
            { text: 'Integration Patterns', link: '/guide/integration' },
            { text: 'Troubleshooting', link: '/guide/troubleshooting' }
          ]
        }
      ],
      '/api/': [
        {
          text: 'API Reference',
          items: [
            { text: 'Overview', link: '/api/' },
            { text: 'Core Features', link: '/api/features' },
            { text: 'Providers', link: '/api/providers' },
            { text: 'Sandbox Management', link: '/api/sandbox' }
          ]
        }
      ],
      '/cli/': [
        {
          text: 'CLI Reference',
          items: [
            { text: 'Overview', link: '/cli/' },
            { text: 'Commands', link: '/cli/commands' },
            { text: 'Configuration', link: '/cli/configuration' },
            { text: 'Examples', link: '/cli/examples' }
          ]
        }
      ],
      '/examples/': [
        {
          text: 'Examples',
          items: [
            { text: 'Overview', link: '/examples/' },
            { text: 'Basic Usage', link: '/examples/basic' },
            { text: 'Advanced Patterns', link: '/examples/advanced' },
            { text: 'Integration Examples', link: '/examples/integrations' }
          ]
        }
      ],
      '/developer/': [
        {
          text: 'Developer Guide',
          items: [
            { text: 'Overview', link: '/developer/' },
            { text: 'Contributing', link: '/developer/contributing' },
            { text: 'Architecture', link: '/developer/architecture' },
            { text: 'Testing', link: '/developer/testing' }
          ]
        }
      ]
    },

    // Social links
    socialLinks: [
      { icon: 'github', link: 'https://github.com/codegen-sh/grainchain' }
    ],

    // Footer
    footer: {
      message: 'Released under the MIT License.',
      copyright: 'Copyright © 2024 Codegen'
    },

    // Search
    search: {
      provider: 'local'
    },

    // Edit link
    editLink: {
      pattern: 'https://github.com/codegen-sh/grainchain/edit/main/docs/:path',
      text: 'Edit this page on GitHub'
    }
  },

  // Markdown configuration
  markdown: {
    lineNumbers: true,
    theme: {
      light: 'github-light',
      dark: 'github-dark'
    }
  },

  // Head configuration for SEO
  head: [
    ['link', { rel: 'icon', href: '/grainchain/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#10b981' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:locale', content: 'en' }],
    ['meta', { property: 'og:title', content: 'GrainChain Documentation' }],
    ['meta', { property: 'og:site_name', content: 'GrainChain Docs' }],
    ['meta', { property: 'og:url', content: 'https://codegen-sh.github.io/grainchain/' }],
    ['meta', { property: 'og:description', content: 'Langchain for sandboxes - A powerful framework for building sandbox-aware AI applications' }]
  ]
})

