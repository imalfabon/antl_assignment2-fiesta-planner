import { useState, useEffect } from 'react'
import axios from 'axios'

const CATEGORIES = ['floral', 'balloon', 'centerpiece', 'linen', 'silverware', 'chair_cover']

function CatalogList() {
  const [items, setItems] = useState([])
  const [filter, setFilter] = useState('')
  const [form, setForm] = useState({ name: '', category: 'floral', description: '', unit_cost: '', unit_price: '', stock_qty: '' })
  const [editingId, setEditingId] = useState(null)
  const [error, setError] = useState(null)

  const load = async () => {
    try {
      const url = filter ? `/api/catalog?category=${filter}` : '/api/catalog'
      const res = await axios.get(url)
      setItems(res.data)
      setError(null)
    } catch (err) {
      setError('Failed to load catalog')
    }
  }

  useEffect(() => { load() }, [filter])

  const resetForm = () => {
    setForm({ name: '', category: 'floral', description: '', unit_cost: '', unit_price: '', stock_qty: '' })
    setEditingId(null)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    const payload = {
      ...form,
      unit_cost: parseFloat(form.unit_cost) || 0,
      unit_price: parseFloat(form.unit_price) || 0,
      stock_qty: parseInt(form.stock_qty) || 0,
    }
    try {
      if (editingId) {
        await axios.put(`/api/catalog/${editingId}`, payload)
      } else {
        await axios.post('/api/catalog', payload)
      }
      resetForm()
      load()
    } catch (err) {
      setError('Failed to save item')
    }
  }

  const handleEdit = (item) => {
    setForm({
      name: item.name, category: item.category, description: item.description || '',
      unit_cost: item.unit_cost.toString(), unit_price: item.unit_price.toString(),
      stock_qty: item.stock_qty.toString(),
    })
    setEditingId(item.id)
  }

  const handleDelete = async (id) => {
    if (!confirm('Delete this item?')) return
    try {
      await axios.delete(`/api/catalog/${id}`)
      load()
    } catch (err) {
      setError('Failed to delete item')
    }
  }

  const formatCategory = (cat) => cat.replace('_', ' ').replace(/\b\w/g, c => c.toUpperCase())

  return (
    <div>
      <h2>Catalog</h2>

      {error && <div className="error-message"><p>⚠ {error}</p></div>}

      <div className="filter-bar">
        <label>Filter: </label>
        <select value={filter} onChange={e => setFilter(e.target.value)}>
          <option value="">All Categories</option>
          {CATEGORIES.map(c => <option key={c} value={c}>{formatCategory(c)}</option>)}
        </select>
      </div>

      <form className="inline-form" onSubmit={handleSubmit}>
        <input placeholder="Name *" value={form.name} onChange={e => setForm({...form, name: e.target.value})} required />
        <select value={form.category} onChange={e => setForm({...form, category: e.target.value})}>
          {CATEGORIES.map(c => <option key={c} value={c}>{formatCategory(c)}</option>)}
        </select>
        <input placeholder="Description" value={form.description} onChange={e => setForm({...form, description: e.target.value})} />
        <input placeholder="Cost" type="number" step="0.01" value={form.unit_cost} onChange={e => setForm({...form, unit_cost: e.target.value})} />
        <input placeholder="Price" type="number" step="0.01" value={form.unit_price} onChange={e => setForm({...form, unit_price: e.target.value})} />
        <input placeholder="Stock" type="number" value={form.stock_qty} onChange={e => setForm({...form, stock_qty: e.target.value})} />
        <button type="submit">{editingId ? 'Update' : 'Add'}</button>
        {editingId && <button type="button" onClick={resetForm}>Cancel</button>}
      </form>

      <table className="data-table">
        <thead>
          <tr>
            <th>Name</th>
            <th>Category</th>
            <th>Description</th>
            <th>Cost</th>
            <th>Price</th>
            <th>Stock</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {items.map(item => (
            <tr key={item.id}>
              <td>{item.name}</td>
              <td>{formatCategory(item.category)}</td>
              <td>{item.description}</td>
              <td>${item.unit_cost.toFixed(2)}</td>
              <td>${item.unit_price.toFixed(2)}</td>
              <td>{item.stock_qty}</td>
              <td>
                <button className="btn-sm" onClick={() => handleEdit(item)}>Edit</button>
                <button className="btn-sm btn-danger" onClick={() => handleDelete(item.id)}>Del</button>
              </td>
            </tr>
          ))}
          {items.length === 0 && <tr><td colSpan="7" style={{textAlign:'center'}}>No items</td></tr>}
        </tbody>
      </table>
    </div>
  )
}

export default CatalogList
