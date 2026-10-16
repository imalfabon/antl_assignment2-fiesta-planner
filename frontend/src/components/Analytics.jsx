import { useState, useEffect } from 'react'
import axios from 'axios'

function Analytics() {
  const [topItems, setTopItems] = useState([])
  const [revenue, setRevenue] = useState([])
  const [seasonal, setSeasonal] = useState([])
  const [margins, setMargins] = useState([])
  const [error, setError] = useState(null)

  useEffect(() => {
    const load = async () => {
      try {
        const [tiRes, revRes, seaRes, marRes] = await Promise.all([
          axios.get('/api/analytics/top-items'),
          axios.get('/api/analytics/revenue'),
          axios.get('/api/analytics/seasonal'),
          axios.get('/api/analytics/margins'),
        ])
        setTopItems(tiRes.data)
        setRevenue(revRes.data)
        setSeasonal(seaRes.data)
        setMargins(marRes.data)
        setError(null)
      } catch (err) {
        setError('Failed to load analytics')
      }
    }
    load()
  }, [])

  const monthName = (m) => {
    const months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
    return months[parseInt(m) - 1] || m
  }

  const formatType = (t) => t.charAt(0).toUpperCase() + t.slice(1)

  return (
    <div>
      <h2>Analytics</h2>

      {error && <div className="error-message"><p>⚠ {error}</p></div>}

      <div className="analytics-grid">
        {/* Top Items */}
        <div className="card">
          <h3>Most Requested Items</h3>
          <table className="data-table">
            <thead>
              <tr><th>Item</th><th>Category</th><th>Total Qty</th><th>Events</th></tr>
            </thead>
            <tbody>
              {topItems.map((item, i) => (
                <tr key={i}>
                  <td>{item.name}</td>
                  <td>{item.category}</td>
                  <td>{item.total_qty}</td>
                  <td>{item.event_count}</td>
                </tr>
              ))}
              {topItems.length === 0 && <tr><td colSpan="4" style={{textAlign:'center'}}>No data</td></tr>}
            </tbody>
          </table>
        </div>

        {/* Revenue by Event Type */}
        <div className="card">
          <h3>Revenue by Event Type</h3>
          <table className="data-table">
            <thead>
              <tr><th>Type</th><th>Events</th><th>Revenue</th></tr>
            </thead>
            <tbody>
              {revenue.map((r, i) => (
                <tr key={i}>
                  <td>{formatType(r.event_type)}</td>
                  <td>{r.event_count}</td>
                  <td>${r.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                </tr>
              ))}
              {revenue.length === 0 && <tr><td colSpan="3" style={{textAlign:'center'}}>No data</td></tr>}
            </tbody>
          </table>
        </div>

        {/* Seasonal Demand */}
        <div className="card">
          <h3>Seasonal Demand</h3>
          <table className="data-table">
            <thead>
              <tr><th>Month</th><th>Events</th><th>Revenue</th></tr>
            </thead>
            <tbody>
              {seasonal.map((s, i) => (
                <tr key={i}>
                  <td>{monthName(s.month)}</td>
                  <td>{s.event_count}</td>
                  <td>${s.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                </tr>
              ))}
              {seasonal.length === 0 && <tr><td colSpan="3" style={{textAlign:'center'}}>No data</td></tr>}
            </tbody>
          </table>
        </div>

        {/* Margins */}
        <div className="card">
          <h3>Cost vs Price Margins</h3>
          <table className="data-table">
            <thead>
              <tr><th>Event</th><th>Type</th><th>Date</th><th>Revenue</th><th>Cost</th><th>Margin</th><th>%</th></tr>
            </thead>
            <tbody>
              {margins.map((m, i) => {
                const margin = m.total_revenue - m.total_cost
                const pct = m.total_revenue > 0 ? (margin / m.total_revenue * 100) : 0
                return (
                  <tr key={i}>
                    <td>{m.client_name}</td>
                    <td>{formatType(m.event_type)}</td>
                    <td>{m.event_date}</td>
                    <td>${m.total_revenue.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    <td>${m.total_cost.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    <td>${margin.toLocaleString('en-US', {minimumFractionDigits: 2})}</td>
                    <td>{pct.toFixed(1)}%</td>
                  </tr>
                )
              })}
              {margins.length === 0 && <tr><td colSpan="7" style={{textAlign:'center'}}>No data</td></tr>}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default Analytics
