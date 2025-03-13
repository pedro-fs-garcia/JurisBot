export default function Header() {    

    return (
      <header className="bg-gray-900 text-white p-4">
        <div className="container mx-auto flex justify-between items-center">
          <h1 className="text-xl font-bold">JurisBot</h1>
          <nav>
            <ul className="flex space-x-4">
              <li>
                <a href="/" className="hover:underline">Home</a>
              </li>
              <li>
                <a href="/dashboard" className="hover:underline">Dashboard</a>
              </li>
            </ul>
          </nav>
        </div>
      </header>
    );
  };
