import { useState, useEffect } from 'react'
import axios from 'axios'

function CateringList() {
  const [packages, setPackages] = useState([])
  const [filter, setFilter] = useState('')
  const [form, setForm] = useState({ name: '', type: 'food', description: '', price_per_person: '', min_guests: '' })
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    try {
      const url = filter ? `/api/catering?type=${filter}` : '/api/catering'
      const res = await axios.get(url)
      setPackages(res.data)
      setError(null)
    } catch (err) {
      setError('Failed to load catering packages')
    }
  }

  useEffect(() => { load() }, [filter])

  const resetForm = () => {
    setForm({ name: '', type: 'food', description: '', price_per_person: '', min_guests: '' })
    setEditingId(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      price_per_person: parseFloat(form.price_per_person) || 0,
      min_guests: parseInt(form.min_guests) || 1,
    }
    try {
      if (editingId) {
        await axios.put(`/api/catering/${editingId}`, payload)
      } else {
        await axios.post('/api/catering', payload)
      }
      resetForm()
      load()
    } catch (err) {
      setError('Failed to save package')
    }
  }

  const handleEdit = (pkg) => {
    setForm({
      name: pkg.name, type: pkg.type, description: pkg.description || '',
      price_per_person: pkg.price_per_person.toString(), min_guests: pkg.min_guests.toString(),
    })
    setEditingId(pkg.id)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this package?')) return
    try {
      await axios.delete(`/api/catering/${id}`)
      load()
    } catch (err) {
      setError('Failed to delete package')
    }
  }

  return (
    <div>
      <h2>Catering Packages</h2>

      {error && <div className="error-message"><p>⚠ {error}</p></div>}

      <div className="filter-bar">
        <label>Filter: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="">All Types</option>
          <option value="food">Food</option>
          <option value="beverage">Beverage</option>
        </select>
      </div>

      <form className="inline-form" onSubmit={handleSubmit}>
        <input placeholder="Name *" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
        <select value={form.type} onChange={e => setForm({...form, type: e.target.value})}>
          <option value="food">Food</option>
          <option value="beverage">Beverage</option>
        </select>
        <input placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
        <input placeholder="$/person" type="number" step="0.01" value={form.price_per_person} onChange={e => setForm({...form, price_per_person: e.target.value})} />
        <input placeholder="Min guests" type="number" value={form.min_guests} onChange={e => setForm({...form, min_guests: e.target.value})} />
        <button type="submit">{editingId ? 'Update' : 'Add'}</button>
        {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Type</th>
            <th>Description</th>
            <th>$/Person</th>
            <th>Min Guests</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {packages.map(pkg => (
            <tr key={pkg.id}>
              <td>{pkg.name}</td>
              <td>{pkg.type.charAt(0).toUpperCase() + pkg.type.slice(1)}</td>
              <td>{pkg.description}</td>
              <td>${pkg.price_per_person.toFixed(2)}</td>
              <td>{pkg.min_guests}</td>
              <td>
                <button className="btn-sm" onClick={() => handleEdit(pkg)}>Edit</button>
                <button className="btn-sm btn-danger" onClick={() => handleDelete(pkg.id)}>Del</button>
              </td>
            </tr>
          ))}
          {packages.length === 0 && <tr><td colSpan="6" style={{textAlign:'center'}}>No packages</td></tr>}
        </tbody>
      </table>
    </div>
  )
}

export default CateringList
