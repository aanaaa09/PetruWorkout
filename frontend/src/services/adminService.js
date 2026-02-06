// frontend/src/services/adminService.js
import axios from 'axios'

const API_URL = 'https://petruworkout-production.up.railway.app/api'

export const deleteUser = async (userId) => {
  const token = localStorage.getItem('admin_token')
  const response = await axios.delete(
    `${API_URL}/admin/users/${userId}`,
    { headers: { 'token': token } }
  )
  return response.data
}
