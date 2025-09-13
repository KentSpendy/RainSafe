import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import API from ".././services/api"; // Adjusted import path
import { logout } from ".././services/auth";

export default function ProfileTest() {
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    async function fetchProfile() {
      try {
        const res = await API.get("/auth/profile/");
        setProfile(res.data);
      } catch (err) {
        setError(err?.response?.data || "Error fetching profile");
      }
    }
    fetchProfile();
  }, []);

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  if (error) {
    return <div className="p-4 text-red-600">Error: {JSON.stringify(error)}</div>;
  }

  if (!profile) {
    return <div className="p-4">Loading...</div>;
  }

  return (
    <div className="p-4">
      <h2 className="text-xl font-bold mb-4">Your Profile</h2>
      <pre className="bg-gray-100 p-4 rounded-lg">{JSON.stringify(profile, null, 2)}</pre>
      <button
        onClick={handleLogout}
        className="mt-4 bg-red-600 text-white px-4 py-2 rounded-lg"
      >
        Logout
      </button>
    </div>
  );
}
