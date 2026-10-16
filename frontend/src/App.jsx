import { useState } from 'react'
import './App.css'
import ClientList from './components/ClientList'
import CatalogList from './components/CatalogList'
import CateringList from './components/CateringList'
import EventList from './components/EventList'
import Analytics from './components/Analytics'

const TABS = ['Clients', 'Catalog', 'Catering', 'Events', 'Analytics']

function App() {
  const [activeTab, setActiveTab] = useState('Clients')

  return (
    <>
      <header className="app-header">
        <h1>Fiesta Planner</h1>
        <p className="subtitle">Event Planning &amp; Arrangement Management</p>
      </header>

      <nav className="tab-bar">
        {TABS.map(tab => (
          <button
            key={tab}
            className={`tab-btn ${activeTab === tab ? 'active' : ''}`}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </nav>

      <main className="app-main">
        {activeTab === 'Clients' && <ClientList />}
        {activeTab === 'Catalog' && <CatalogList />}
        {activeTab === 'Catering' && <CateringList />}
        {activeTab === 'Events' && <EventList />}
        {activeTab === 'Analytics' && <Analytics />}
      </main>
    </>
  )
}

export default App
