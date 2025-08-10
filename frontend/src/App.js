import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import axios from "axios";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Auth Context
const AuthContext = createContext();

const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchCurrentUser();
    } else {
      setLoading(false);
    }
  }, []);

  const fetchCurrentUser = async () => {
    try {
      const response = await axios.get(`${API}/me`);
      setUser(response.data);
    } catch (error) {
      console.error('Failed to fetch user:', error);
      localStorage.removeItem('token');
      delete axios.defaults.headers.common['Authorization'];
    } finally {
      setLoading(false);
    }
  };

  const login = async (email, password) => {
    try {
      const response = await axios.post(`${API}/login`, { email, password });
      const { access_token, user: userData } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(userData);
      
      return userData;
    } catch (error) {
      throw error;
    }
  };

  const register = async (userData) => {
    try {
      const response = await axios.post(`${API}/register`, userData);
      const { access_token, user: newUser } = response.data;
      
      localStorage.setItem('token', access_token);
      axios.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      setUser(newUser);
      
      return newUser;
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('token');
    delete axios.defaults.headers.common['Authorization'];
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, register, logout, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

// Login Component
const LoginForm = ({ onSwitchToRegister }) => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await login(email, password);
    } catch (error) {
      setError(error.response?.data?.detail || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-red-600 mb-2">🩸 Blood Alert System</h1>
          <p className="text-gray-600">Sign in to save lives</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Password</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-200 font-medium disabled:opacity-50"
          >
            {loading ? 'Signing In...' : 'Sign In'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Don't have an account?{' '}
            <button
              onClick={onSwitchToRegister}
              className="text-red-600 font-medium hover:text-red-700"
            >
              Register here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

// Registration Component
const RegisterForm = ({ onSwitchToLogin }) => {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    name: '',
    role: 'donor',
    phone: '',
    hospital_name: '',
    hospital_address: '',
    blood_type: '',
    city: '',
    latitude: null,
    longitude: null
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    // Get location for donors
    if (formData.role === 'donor' && navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        async (position) => {
          const updatedData = {
            ...formData,
            latitude: position.coords.latitude,
            longitude: position.coords.longitude
          };
          await submitForm(updatedData);
        },
        async () => {
          // Continue without location if permission denied
          await submitForm(formData);
        }
      );
    } else {
      await submitForm(formData);
    }
  };

  const submitForm = async (data) => {
    try {
      await register(data);
    } catch (error) {
      setError(error.response?.data?.detail || 'Registration failed');
      setLoading(false);
    }
  };

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-red-50 to-red-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-red-600 mb-2">🩸 Join Blood Alert System</h1>
          <p className="text-gray-600">Register to help save lives</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">I am a:</label>
            <select
              name="role"
              value={formData.role}
              onChange={handleChange}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="donor">Blood Donor</option>
              <option value="hospital_staff">Hospital Staff</option>
            </select>
          </div>

          <div className="grid grid-cols-1 gap-4">
            <input
              type="text"
              name="name"
              placeholder="Full Name"
              value={formData.name}
              onChange={handleChange}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
            <input
              type="email"
              name="email"
              placeholder="Email Address"
              value={formData.email}
              onChange={handleChange}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
            <input
              type="password"
              name="password"
              placeholder="Password"
              value={formData.password}
              onChange={handleChange}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
            <input
              type="tel"
              name="phone"
              placeholder="Phone Number"
              value={formData.phone}
              onChange={handleChange}
              className="px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>

          {formData.role === 'hospital_staff' && (
            <div className="space-y-4">
              <input
                type="text"
                name="hospital_name"
                placeholder="Hospital Name"
                value={formData.hospital_name}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
              <input
                type="text"
                name="hospital_address"
                placeholder="Hospital Address"
                value={formData.hospital_address}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              />
            </div>
          )}

          {formData.role === 'donor' && (
            <div className="space-y-4">
              <select
                name="blood_type"
                value={formData.blood_type}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              >
                <option value="">Select Blood Type</option>
                {bloodTypes.map(type => (
                  <option key={type} value={type}>{type}</option>
                ))}
              </select>
              <input
                type="text"
                name="city"
                placeholder="City"
                value={formData.city}
                onChange={handleChange}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                required
              />
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-200 font-medium disabled:opacity-50"
          >
            {loading ? 'Registering...' : 'Register'}
          </button>
        </form>

        <div className="mt-6 text-center">
          <p className="text-gray-600">
            Already have an account?{' '}
            <button
              onClick={onSwitchToLogin}
              className="text-red-600 font-medium hover:text-red-700"
            >
              Sign in here
            </button>
          </p>
        </div>
      </div>
    </div>
  );
};

// Hospital Dashboard
const HospitalDashboard = () => {
  const { user, logout } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [showCreateAlert, setShowCreateAlert] = useState(false);
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [responses, setResponses] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [alertsRes, statsRes] = await Promise.all([
        axios.get(`${API}/alerts`),
        axios.get(`${API}/dashboard/stats`)
      ]);
      setAlerts(alertsRes.data);
      setStats(statsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchResponses = async (alertId) => {
    try {
      const response = await axios.get(`${API}/alerts/${alertId}/responses`);
      setResponses(response.data);
    } catch (error) {
      console.error('Failed to fetch responses:', error);
    }
  };

  const handleAlertClick = (alert) => {
    setSelectedAlert(alert);
    fetchResponses(alert.id);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🏥 Hospital Dashboard</h1>
              <p className="text-gray-600">{user?.hospital_name}</p>
            </div>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                📊
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_alerts || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100 text-red-600">
                🚨
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.active_alerts || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 text-green-600">
                ✅
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Available Donors</p>
                <p className="text-2xl font-bold text-gray-900">{stats.available_responses || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-purple-100 text-purple-600">
                📧
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Total Responses</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_responses || 0}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Alerts List */}
          <div className="lg:col-span-2">
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                <h2 className="text-lg font-semibold text-gray-900">Blood Alerts</h2>
                <button
                  onClick={() => setShowCreateAlert(true)}
                  className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
                >
                  + Create Alert
                </button>
              </div>
              <div className="p-6">
                {alerts.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No alerts created yet</p>
                ) : (
                  <div className="space-y-4">
                    {alerts.map((alert) => (
                      <div
                        key={alert.id}
                        onClick={() => handleAlertClick(alert)}
                        className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:bg-gray-50 transition duration-200"
                      >
                        <div className="flex justify-between items-start mb-2">
                          <div>
                            <h3 className="font-semibold text-gray-900">
                              {alert.blood_type} Blood Needed
                            </h3>
                            <p className="text-sm text-gray-600">
                              {alert.units_needed} units • {alert.urgency_level} priority
                            </p>
                          </div>
                          <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                            alert.status === 'active' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-gray-100 text-gray-800'
                          }`}>
                            {alert.status}
                          </span>
                        </div>
                        {alert.description && (
                          <p className="text-sm text-gray-700 mb-2">{alert.description}</p>
                        )}
                        <p className="text-xs text-gray-500">
                          Created: {new Date(alert.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Alert Details/Responses */}
          <div className="lg:col-span-1">
            {selectedAlert ? (
              <div className="bg-white rounded-lg shadow">
                <div className="px-6 py-4 border-b border-gray-200">
                  <h2 className="text-lg font-semibold text-gray-900">Donor Responses</h2>
                  <p className="text-sm text-gray-600">{selectedAlert.blood_type} Alert</p>
                </div>
                <div className="p-6">
                  {responses.length === 0 ? (
                    <p className="text-gray-500 text-center py-4">No responses yet</p>
                  ) : (
                    <div className="space-y-3">
                      {responses.map((response) => (
                        <div key={response.id} className="border border-gray-200 rounded-lg p-3">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-medium text-gray-900">{response.donor_name}</h4>
                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                              response.response === 'available' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {response.response}
                            </span>
                          </div>
                          {response.donor_phone && (
                            <p className="text-sm text-gray-600">📞 {response.donor_phone}</p>
                          )}
                          {response.message && (
                            <p className="text-sm text-gray-700 mt-2">{response.message}</p>
                          )}
                          <p className="text-xs text-gray-500 mt-2">
                            {new Date(response.responded_at).toLocaleString()}
                          </p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <p className="text-gray-500">Select an alert to view responses</p>
              </div>
            )}
          </div>
        </div>
      </main>

      {/* Create Alert Modal */}
      {showCreateAlert && (
        <CreateAlertModal 
          onClose={() => setShowCreateAlert(false)} 
          onSuccess={() => {
            setShowCreateAlert(false);
            fetchData();
          }}
        />
      )}
    </div>
  );
};

// Create Alert Modal
const CreateAlertModal = ({ onClose, onSuccess }) => {
  const [formData, setFormData] = useState({
    blood_type: '',
    units_needed: 1,
    urgency_level: 'medium',
    description: '',
    radius_km: 50
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const bloodTypes = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-'];

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      await axios.post(`${API}/alerts`, formData);
      onSuccess();
    } catch (error) {
      setError(error.response?.data?.detail || 'Failed to create alert');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-2xl shadow-xl p-8 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-900">🩸 Create Blood Alert</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-2xl"
          >
            ×
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Blood Type</label>
            <select
              value={formData.blood_type}
              onChange={(e) => setFormData({...formData, blood_type: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            >
              <option value="">Select Blood Type</option>
              {bloodTypes.map(type => (
                <option key={type} value={type}>{type}</option>
              ))}
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Units Needed</label>
            <input
              type="number"
              min="1"
              value={formData.units_needed}
              onChange={(e) => setFormData({...formData, units_needed: parseInt(e.target.value)})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Urgency Level</label>
            <select
              value={formData.urgency_level}
              onChange={(e) => setFormData({...formData, urgency_level: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            >
              <option value="medium">Medium</option>
              <option value="high">High</option>
              <option value="critical">Critical</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Description</label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({...formData, description: e.target.value})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
              rows="3"
              placeholder="Describe the emergency or specific requirements..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Search Radius (km)</label>
            <input
              type="number"
              min="1"
              max="200"
              value={formData.radius_km}
              onChange={(e) => setFormData({...formData, radius_km: parseFloat(e.target.value)})}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
            />
          </div>

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg text-sm">
              {error}
            </div>
          )}

          <div className="flex space-x-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 bg-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-400 transition duration-200"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="flex-1 bg-red-600 text-white py-3 px-4 rounded-lg hover:bg-red-700 transition duration-200 disabled:opacity-50"
            >
              {loading ? 'Creating...' : 'Create Alert'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

// Donor Dashboard
const DonorDashboard = () => {
  const { user, logout } = useAuth();
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState({});
  const [mockEmails, setMockEmails] = useState([]);
  const [loading, setLoading] = useState(true);
  const [successMessage, setSuccessMessage] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      const [alertsRes, statsRes, emailsRes] = await Promise.all([
        axios.get(`${API}/alerts`),
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/mock-emails`)
      ]);
      setAlerts(alertsRes.data);
      setStats(statsRes.data);
      setMockEmails(emailsRes.data);
    } catch (error) {
      console.error('Failed to fetch data:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleResponse = async (alertId, response, message = '') => {
    try {
      await axios.post(`${API}/alerts/${alertId}/respond`, {
        response,
        message
      });
      
      // Show success message
      if (response === 'available') {
        setSuccessMessage('Response successfully sent. Hospital will reach out to you');
      } else {
        setSuccessMessage('Response recorded. Thank you for letting us know');
      }
      
      // Auto hide message after 5 seconds
      setTimeout(() => setSuccessMessage(''), 5000);
      
      fetchData(); // Refresh data
    } catch (error) {
      console.error('Failed to respond:', error);
      alert('Failed to submit response');
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">🩸 Donor Dashboard</h1>
              <p className="text-gray-600">{user?.name} • {user?.blood_type}</p>
            </div>
            <button
              onClick={logout}
              className="bg-red-600 text-white px-4 py-2 rounded-lg hover:bg-red-700 transition duration-200"
            >
              Sign Out
            </button>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Stats Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-red-100 text-red-600">
                🚨
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Active Alerts</p>
                <p className="text-2xl font-bold text-gray-900">{stats.active_alerts_for_blood_type || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-green-100 text-green-600">
                ✅
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">My Responses</p>
                <p className="text-2xl font-bold text-gray-900">{stats.total_responses || 0}</p>
              </div>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center">
              <div className="p-3 rounded-full bg-blue-100 text-blue-600">
                💝
              </div>
              <div className="ml-4">
                <p className="text-sm font-medium text-gray-600">Available Times</p>
                <p className="text-2xl font-bold text-gray-900">{stats.available_responses || 0}</p>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Active Alerts */}
          <div>
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">Blood Alerts for {user?.blood_type}</h2>
              </div>
              <div className="p-6">
                {alerts.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No active alerts for your blood type</p>
                ) : (
                  <div className="space-y-4">
                    {alerts.map((alert) => (
                      <div key={alert.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-3">
                          <div>
                            <h3 className="font-semibold text-gray-900">🏥 {alert.hospital_name}</h3>
                            <p className="text-sm text-gray-600">
                              Needs {alert.units_needed} units of {alert.blood_type}
                            </p>
                            <span className={`inline-block px-2 py-1 rounded-full text-xs font-medium mt-1 ${
                              alert.urgency_level === 'critical' 
                                ? 'bg-red-100 text-red-800' 
                                : alert.urgency_level === 'high'
                                ? 'bg-orange-100 text-orange-800'
                                : 'bg-yellow-100 text-yellow-800'
                            }`}>
                              {alert.urgency_level} priority
                            </span>
                          </div>
                        </div>
                        
                        {alert.description && (
                          <p className="text-sm text-gray-700 mb-3">{alert.description}</p>
                        )}
                        
                        <div className="flex space-x-2">
                          <button
                            onClick={() => handleResponse(alert.id, 'available', 'I am available to donate')}
                            className="flex-1 bg-green-600 text-white py-2 px-4 rounded-lg hover:bg-green-700 transition duration-200 text-sm"
                          >
                            ✅ I'm Available
                          </button>
                          <button
                            onClick={() => handleResponse(alert.id, 'not_available', 'Sorry, I am not available')}
                            className="flex-1 bg-gray-400 text-white py-2 px-4 rounded-lg hover:bg-gray-500 transition duration-200 text-sm"
                          >
                            ❌ Not Available
                          </button>
                        </div>
                        
                        <p className="text-xs text-gray-500 mt-3">
                          Created: {new Date(alert.created_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Mock Email Notifications */}
          <div>
            <div className="bg-white rounded-lg shadow">
              <div className="px-6 py-4 border-b border-gray-200">
                <h2 className="text-lg font-semibold text-gray-900">📧 Email Notifications (Demo)</h2>
              </div>
              <div className="p-6">
                {mockEmails.length === 0 ? (
                  <p className="text-gray-500 text-center py-8">No email notifications yet</p>
                ) : (
                  <div className="space-y-4 max-h-96 overflow-y-auto">
                    {mockEmails.map((email) => (
                      <div key={email.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex justify-between items-start mb-2">
                          <h4 className="font-medium text-gray-900 text-sm">{email.subject}</h4>
                          <span className="text-xs text-green-600 bg-green-100 px-2 py-1 rounded-full">
                            {email.status}
                          </span>
                        </div>
                        <p className="text-xs text-gray-600 mb-2">To: {email.to_email}</p>
                        <p className="text-sm text-gray-700 mb-2 line-clamp-3">
                          {email.body.substring(0, 150)}...
                        </p>
                        <p className="text-xs text-gray-500">
                          {new Date(email.sent_at).toLocaleString()}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

// Main App Component
function App() {
  const [showRegister, setShowRegister] = useState(false);

  return (
    <AuthProvider>
      <AuthenticatedApp 
        showRegister={showRegister}
        setShowRegister={setShowRegister}
      />
    </AuthProvider>
  );
}

const AuthenticatedApp = ({ showRegister, setShowRegister }) => {
  const { user, loading } = useAuth();

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-red-600"></div>
          <p className="mt-4 text-gray-600">Loading...</p>
        </div>
      </div>
    );
  }

  if (!user) {
    if (showRegister) {
      return <RegisterForm onSwitchToLogin={() => setShowRegister(false)} />;
    }
    return <LoginForm onSwitchToRegister={() => setShowRegister(true)} />;
  }

  if (user.role === 'hospital_staff') {
    return <HospitalDashboard />;
  }

  return <DonorDashboard />;
};

export default App;