import { NavLink } from "react-router-dom";

export function NavTabs() {
  return (
    <nav className="nav-tabs">
      <NavLink to="/" end className={({ isActive }) => (isActive ? "is-active" : "")}>
        Browse
      </NavLink>
      <NavLink to="/shortlist" className={({ isActive }) => (isActive ? "is-active" : "")}>
        Shortlist
      </NavLink>
    </nav>
  );
}
