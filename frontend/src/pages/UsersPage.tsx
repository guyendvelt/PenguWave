import { useEffect, useState } from "react";
import { createUser, deleteUser, getUsers } from "../api";
import { User } from "../types";

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [newEmail, setNewEmail] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [newRole, setNewRole] = useState("viewer");

  const loadUsers = () => {
    setLoading(true);
    getUsers()
      .then((data) => {
        setUsers(data);
        setError(null);
      })
      .catch((err: unknown) =>
        setError(err instanceof Error ? err.message : "Failed to load users")
      )
      .finally(() => setLoading(false));
  };

  useEffect(loadUsers, []);

  const handleAddUser = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newEmail || !newPassword) return;
    try {
      await createUser({ email: newEmail, password: newPassword, role: newRole });
      setNewEmail("");
      setNewPassword("");
      setNewRole("viewer");
      setShowForm(false);
      loadUsers();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to create user");
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteUser(id);
      loadUsers();
    } catch (err: unknown) {
      setError(err instanceof Error ? err.message : "Failed to delete user");
    }
  };

  return (
    <div className="page-container">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 16 }}>
        <h1>User Management</h1>
        <button className="btn-primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? "Cancel" : "Add User"}
        </button>
      </div>

      {error && (
        <p style={{ color: "red" }} role="alert">
          {error}
        </p>
      )}

      {showForm && (
        <div style={{ border: "1px solid #ddd", padding: 16, marginBottom: 20, background: "#fafafa" }}>
          <h3 style={{ marginBottom: 12 }}>New User</h3>
          <form onSubmit={handleAddUser}>
            <div style={{ marginBottom: 8 }}>
              <label>Email</label>
              <input
                type="email"
                value={newEmail}
                onChange={(e) => setNewEmail(e.target.value)}
                placeholder="user@penguwave.io"
                required
              />
            </div>
            <div style={{ marginBottom: 8 }}>
              <label>Password</label>
              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                placeholder="password (min 8 chars)"
                required
              />
            </div>
            <div style={{ marginBottom: 12 }}>
              <label>Role</label>
              <select value={newRole} onChange={(e) => setNewRole(e.target.value)}>
                <option value="admin">Admin</option>
                <option value="viewer">Viewer</option>
              </select>
            </div>
            <button type="submit" className="btn-primary">
              Create User
            </button>
          </form>
        </div>
      )}

      {loading && <p style={{ color: "#666" }}>Loading users…</p>}

      <table>
        <thead>
          <tr>
            <th>Email</th>
            <th>Role</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          {users.map((user) => (
            <tr key={user.id}>
              <td>{user.email}</td>
              <td>{user.role}</td>
              <td>
                <span style={{ color: user.status === "active" ? "green" : "#999" }}>
                  {user.status}
                </span>
              </td>
              <td>
                <a
                  href="#"
                  onClick={(e) => {
                    e.preventDefault();
                    handleDelete(user.id);
                  }}
                  style={{ color: "red" }}
                >
                  Delete
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      {!loading && users.length === 0 && <p style={{ color: "#999" }}>No users.</p>}
    </div>
  );
}
