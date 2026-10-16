import { useState, useEffect } from 'react'
import axios from 'axios'

function ClientList() {
  const [clients, setClients] = useState([])
  const [form, setForm] = useState({ name: '', phone: '', email: '', notes: '' })
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    try {
      const res = await axios.get('/api/clients')
      setClients(res.data)
      setError(null)
    } catch (err) {
      setError('Failed to load clients')
    }
  }

  useEffect(() => { load() }, [])

  const resetForm = () => {
    setForm({ name: '', phone: '', email: '', notes: '' })
    setEditingId(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    try {
      if (editingId) {
        await axios.put(`/api/clients/${editingId}`, form)
      } else {
        await axios.post('/api/clients', form)
      }
      resetForm()
      load()
    } catch (err) {
      setError('Failed to save client')
    }
  }

  const handleEdit = (client) => {
    setForm({ name: client.name, phone: client.phone || '', email: client.email || '', notes: client.notes || '' })
    setEditingId(client.id)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this client?')) return
    try {
      await axios.delete(`/api/clients/${id}`)
      load()
    } catch (err) {
      setError('Failed to delete client')
    }
  }

  return (
    <div>
      <h2>Clients</h2>

      {error && <div className="error-message"><p>⚠ {error}</p></div>}

      <form className="inline-form" onSubmit={handleSubmit}>
        <input placeholder="Name *" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
        <input placeholder="Phone" value={form.phone} onChange={e => setForm({...form, phone: e.target.value})} />
        <input placeholder="Email" value={form.email} onChange={e => setForm({...form, email: e.target.value})} />
        <input placeholder="Notes" value={form.notes} onChange={e => setForm({...form, notes: e.target.value})} />
        <button type="submit">{editingId ? 'Update' : 'Add'}</button>
        {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Phone</th>
            <th>Email</th>
            <th>Notes</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {clients.map(c => (
            <tr key={c.id}>
              <td>{c.name}</td>
              <td>{c.phone}</td>
              <td>{c.email}</td>
              <td>{c.notes}</td>
              <td>
                <button className="btn-sm" onClick={() => handleEdit(c)}>Edit</button>
                <button className="btn-sm btn-danger" onClick={() => handleDelete(c.id)}>Del</button>
              </td>
            </tr>
          ))}
          {clients.length === 0 && <tr><td colSpan="5" style={{textAlign:'center'}}>No clients yet</td></tr>}
        </tbody>
      </table>
    </div>
  )
}

export default ClientList
