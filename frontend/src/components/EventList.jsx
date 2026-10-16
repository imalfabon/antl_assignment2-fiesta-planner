import { useState, useEffect } from 'react'
import axios from 'axios'

const EVENT_TYPES = ['quinceañera', 'wedding', 'birthday', 'special']
const STATUSES = ['draft', 'confirmed', 'completed', 'cancelled']

function EventList() {
  const [events, setEvents] = useState([])
  const [clients, setClients] = useState([])
  const [catalogItems, setCatalogItems] = useState([])
  const [cateringPkgs, setCateringPkgs] = useState([])
  const [selectedEvent, setSelectedEvent] = useState(null)
  const [lineItems, setLineItems] = useState([])
  const [form, setForm] = useState({
    client_id: '', event_type: 'quinceañera', event_date: '', venue: '',
    guest_count: '', status: 'draft', special_requirements: ''
  })
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState(null)

  // Line item form
  const [liForm, setLiForm] = useState({ item_type: 'catalog', catalog_item_id: '', catering_package_id: '', quantity: '1' })

  const load = async () => {
    try {
      const [evRes, clRes, catRes, ctrRes] = await Promise.all([
        axios.get('/api/events'),
        axios.get('/api/clients'),
        axios.get('/api/catalog'),
        axios.get('/api/catering'),
      ])
      setEvents(evRes.data)
      setClients(clRes.data)
      setCatalogItems(catRes.data)
      setCateringPkgs(ctrRes.data)
      setError(null)
    } catch (err) {
      setError('Failed to load data')
    }
  }

  useEffect(() => { load() }, [])

  const loadLineItems = async (eventId) => {
    try {
      const res = await axios.get(`/api/events/${eventId}/items`)
      setLineItems(res.data)
    } catch (err) {
      setError('Failed to load line items')
    }
  }

  const resetForm = () => {
    setForm({ client_id: '', event_type: 'quinceañera', event_date: '', venue: '', guest_count: '', status: 'draft', special_requirements: '' })
    setEditingId(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = { ...form, guest_count: parseInt(form.guest_count) || 0 }
    try {
      if (editingId) {
        await axios.put(`/api/events/${editingId}`, payload)
      } else {
        await axios.post('/api/events', payload)
      }
      resetForm()
      load()
    } catch (err) {
      setError('Failed to save event')
    }
  }

  const handleEdit = (ev) => {
    setForm({
      client_id: ev.client_id.toString(), event_type: ev.event_type, event_date: ev.event_date,
      venue: ev.venue || '', guest_count: ev.guest_count.toString(),
      status: ev.status, special_requirements: ev.special_requirements || '',
    })
    setEditingId(ev.id)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this event and all its line items?')) return
    try {
      await axios.delete(`/api/events/${id}`)
      if (selectedEvent === id) { setSelectedEvent(null); setLineItems([]) }
      load()
    } catch (err) {
      setError('Failed to delete event')
    }
  }

  const handleSelectEvent = (id) => {
    setSelectedEvent(id)
    loadLineItems(id)
  }

  const handleAddLineItem = async (e) => {
    e.preventDefault()
    let unit_price = 0
    if (liForm.item_type === 'catalog') {
      const item = catalogItems.find(i => i.id === parseInt(liForm.catalog_item_id))
      unit_price = item ? item.unit_price : 0
    } else {
      const pkg = cateringPkgs.find(p => p.id === parseInt(liForm.catering_package_id))
      unit_price = pkg ? pkg.price_per_person : 0
    }
    try {
      await axios.post(`/api/events/${selectedEvent}/items`, {
        item_type: liForm.item_type,
        catalog_item_id: liForm.item_type === 'catalog' ? parseInt(liForm.catalog_item_id) : null,
        catering_package_id: liForm.item_type === 'catering' ? parseInt(liForm.catering_package_id) : null,
        quantity: parseInt(liForm.quantity) || 1,
        unit_price,
      })
      setLiForm({ item_type: 'catalog', catalog_item_id: '', catering_package_id: '', quantity: '1' })
      loadLineItems(selectedEvent)
    } catch (err) {
      setError('Failed to add line item')
    }
  }

  const handleDeleteLineItem = async (liId) => {
    try {
      await axios.delete(`/api/events/${selectedEvent}/items/${liId}`)
      loadLineItems(selectedEvent)
    } catch (err) {
      setError('Failed to delete line item')
    }
  }

  const formatType = (t) => t.charAt(0).toUpperCase() + t.slice(1)
  const statusClass = (s) => `status-${s}`

  return (
    <div>
      <h2>Events</h2>

      {error && <div className="error-message"><p>⚠ {error}</p></div>}

      <form className="inline-form" onSubmit={handleSubmit}>
        <select value={form.client_id} onChange={e => setForm({...form, client_id: e.target.value})} required>
          <option value="">-- Client --</option>
          {clients.map(c => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        <select value={form.event_type} onChange={e => setForm({...form, event_type: e.target.value})}>
          {EVENT_TYPES.map(t => <option key={t} value={t}>{formatType(t)}</option>)}
        </select>
        <input type="date" value={form.event_date} onChange={e => setForm({...form, event_date: e.target.value})} required />
        <input placeholder="Venue" value={form.venue} onChange={e => setForm({...form, venue: e.target.value})} />
        <input placeholder="Guests" type="number" value={form.guest_count} onChange={e => setForm({...form, guest_count: e.target.value})} />
        <select value={form.status} onChange={e => setForm({...form, status: e.target.value})}>
          {STATUSES.map(s => <option key={s} value={s}>{formatType(s)}</option>)}
        </select>
        <input placeholder="Special requirements" value={form.special_requirements} onChange={e => setForm({...form, special_requirements: e.target.value})} />
        <button type="submit">{editingId ? 'Update' : 'Add'}</button>
        {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Client</th>
            <th>Type</th>
            <th>Date</th>
            <th>Venue</th>
            <th>Guests</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {events.map(ev => (
            <tr key={ev.id} className={selectedEvent === ev.id ? 'row-selected' : ''}>
              <td>{ev.client_name}</td>
              <td>{formatType(ev.event_type)}</td>
              <td>{ev.event_date}</td>
              <td>{ev.venue}</td>
              <td>{ev.guest_count}</td>
              <td><span className={statusClass(ev.status)}>{formatType(ev.status)}</span></td>
              <td>
                <button className="btn-sm" onClick={() => handleSelectEvent(ev.id)}>Items</button>
                <button className="btn-sm" onClick={() => handleEdit(ev)}>Edit</button>
                <button className="btn-sm btn-danger" onClick={() => handleDelete(ev.id)}>Del</button>
              </td>
            </tr>
          ))}
          {events.length === 0 && <tr><td colSpan="7" style={{textAlign:'center'}}>No events</td></tr>}
        </tbody>
      </table>

      {/* Line Items Panel */}
      {selectedEvent && (
        <div className="card" style={{marginTop: '1.5rem'}}>
          <h3>Line Items — Event #{selectedEvent}</h3>

          <form className="inline-form" onSubmit={handleAddLineItem}>
            <select value={liForm.item_type} onChange={e => setLiForm({...liForm, item_type: e.target.value})}>
              <option value="catalog">Catalog Item</option>
              <option value="catering">Catering Package</option>
            </select>

            {liForm.item_type === 'catalog' ? (
              <select value={liForm.catalog_item_id} onChange={e => setLiForm({...liForm, catalog_item_id: e.target.value})} required>
                <option value="">-- Select Item --</option>
                {catalogItems.map(i => <option key={i.id} value={i.id}>{i.name} (${i.unit_price})</option>)}
              </select>
            ) : (
              <select value={liForm.catering_package_id} onChange={e => setLiForm({...liForm, catering_package_id: e.target.value})} required>
                <option value="">-- Select Package --</option>
                {cateringPkgs.map(p => <option key={p.id} value={p.id}>{p.name} (${p.price_per_person}/pp)</option>)}
              </select>
            )}

            <input placeholder="Qty" type="number" min="1" value={liForm.quantity} onChange={e => setLiForm({...liForm, quantity: e.target.value})} style={{width:'80px'}} />
            <button type="submit">Add</button>
          </form>

          <table className="data-table">
            <thead>
              <tr>
                <th>Type</th>
                <th>Item</th>
                <th>Qty</th>
                <th>Unit Price</th>
                <th>Subtotal</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {lineItems.map(li => (
                <tr key={li.id}>
                  <td>{li.item_type === 'catalog' ? 'Catalog' : 'Catering'}</td>
                  <td>{li.catalog_item_name || li.catering_package_name}</td>
                  <td>{li.quantity}</td>
                  <td>${li.unit_price_at_booking.toFixed(2)}</td>
                  <td>${li.subtotal.toFixed(2)}</td>
                  <td><button className="btn-sm btn-danger" onClick={() => handleDeleteLineItem(li.id)}>Del</button></td>
                </tr>
              ))}
              {lineItems.length === 0 && <tr><td colSpan="6" style={{textAlign:'center'}}>No items assigned</td></tr>}
              {lineItems.length > 0 && (
                <tr className="total-row">
                  <td colSpan="4" style={{textAlign:'right'}}><strong>Total:</strong></td>
                  <td><strong>${lineItems.reduce((sum, li) => sum + li.subtotal, 0).toFixed(2)}</strong></td>
                  <td></td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

export default EventList
