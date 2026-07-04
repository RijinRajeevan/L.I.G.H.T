import { Search, Globe } from 'lucide-react'; // Using standard icons for now

export const GovHeader: React.FC = () => {
    return (
        <header className="flex flex-col w-full bg-white shadow-md font-sans">
            {/* Top Government Strip */}
            <div className="bg-[#1b1b1b] text-white text-xs py-1 px-4 md:px-8 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <span>भारत सरकार | Government of India</span>
                </div>
                <div className="flex gap-4">
                    <span className="cursor-pointer hover:underline">Skip to Main Content</span>
                    <span>|</span>
                    <span className="cursor-pointer hover:underline">Screen Reader Access</span>
                    <span>|</span>
                    <div className="flex items-center gap-1 cursor-pointer">
                        <span>A-</span>
                        <span>A</span>
                        <span>A+</span>
                    </div>
                    <span>|</span>
                    <div className="flex items-center gap-1 cursor-pointer bg-blue-700 px-2 rounded">
                        <Globe size={12} />
                        <span>English</span>
                    </div>
                </div>
            </div>

            {/* Main Header with Branding */}
            <div className="flex flex-col md:flex-row items-center justify-between py-4 px-4 md:px-8 bg-white text-gov-text border-b mb-1">
                <div className="flex items-center gap-4">
                    {/* Placeholder for Emblem */}
                    <div className="flex flex-col items-center justify-center w-16 h-20 md:w-20 md:h-24">
                        <img
                            src="https://upload.wikimedia.org/wikipedia/commons/5/55/Emblem_of_India.svg"
                            alt="National Emblem of India"
                            className="w-full h-full object-contain"
                        />
                    </div>

                    <div className="flex flex-col">
                        <h1 className="text-2xl md:text-4xl font-bold text-gov-blue tracking-tight">Nyaya-Setu</h1>
                        <span className="text-sm md:text-base font-medium text-gray-600">Legal Bharat Mission</span>
                        <span className="text-xs text-gray-500 uppercase tracking-wider">Department of Justice, Govt of India</span>
                    </div>
                </div>

                {/* Right Side - Search & Logos */}
                <div className="flex flex-col items-end gap-4 mt-4 md:mt-0">
                    <div className="flex items-center gap-2">
                        <img
                            src="https://upload.wikimedia.org/wikipedia/commons/8/84/Government_of_India_logo.svg"
                            alt="G20/Gov Logo Placeholder"
                            className="h-12 opacity-80"
                        />
                        <img
                            src="https://upload.wikimedia.org/wikipedia/en/9/95/Digital_India_logo.svg"
                            alt="Digital India"
                            className="h-10 opacity-80"
                        />
                    </div>
                    <div className="flex items-center border border-gray-300 rounded overflow-hidden">
                        <input
                            type="text"
                            placeholder="Search..."
                            className="px-3 py-1.5 text-sm w-48 focus:outline-none"
                        />
                        <button className="bg-gov-blue text-white px-3 py-1.5 hover:bg-blue-900 transition-colors">
                            <Search size={16} />
                        </button>
                    </div>
                </div>
            </div>

            {/* Navigation Bar */}
            <nav className="bg-gov-blue text-white">
                <ul className="flex flex-wrap justify-center md:justify-start px-4 md:px-8 text-sm md:text-base font-medium">
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Home</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">About Us</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Services</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Legal Aid</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Acts & Rules</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Statistics</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Media</li>
                    <li className="px-4 py-3 hover:bg-blue-900 cursor-pointer border-r border-blue-800">Contact Us</li>
                </ul>
            </nav>
        </header>
    );
};
