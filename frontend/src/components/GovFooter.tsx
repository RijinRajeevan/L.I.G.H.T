import React from 'react';

export const GovFooter: React.FC = () => {
    return (
        <footer className="bg-[#1b1b1b] text-white pt-10 pb-4 font-sans border-t-4 border-gov-saffron">
            <div className="container mx-auto px-4 md:px-8 grid grid-cols-1 md:grid-cols-4 gap-8 mb-8">
                {/* Column 1 */}
                <div className="flex flex-col gap-2">
                    <h3 className="text-lg font-bold mb-2 border-b border-gray-600 pb-1 inline-block w-full">Quick Links</h3>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Home</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">About The Ministry</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Organisation Structure</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Our Mission</a>
                </div>

                {/* Column 2 */}
                <div className="flex flex-col gap-2">
                    <h3 className="text-lg font-bold mb-2 border-b border-gray-600 pb-1 inline-block w-full">Policies</h3>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">In Terms of Use</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Privacy Policy</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Copyright Policy</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Hyperlinking Policy</a>
                    <a href="#" className="text-sm text-gray-300 hover:text-white hover:underline">Accessibility Statement</a>
                </div>

                {/* Column 3 */}
                <div className="flex flex-col gap-2">
                    <h3 className="text-lg font-bold mb-2 border-b border-gray-600 pb-1 inline-block w-full">Contact</h3>
                    <p className="text-sm text-gray-300">
                        Department of Justice<br />
                        Jaisalmer House, 26, Man Singh Road,<br />
                        New Delhi-110011, India
                    </p>
                    <p className="text-sm text-gray-300 mt-2">
                        Email: helpdesk-nyaya@gov.in
                    </p>
                </div>

                {/* Column 4 - Logos */}
                <div className="flex flex-col items-center justify-start gap-4">
                    <img
                        src="https://upload.wikimedia.org/wikipedia/commons/b/b5/National_Informatics_Centre_Logo.svg"
                        alt="NIC Logo"
                        className="h-12 bg-white p-1 rounded"
                    />
                    <img
                        src="https://upload.wikimedia.org/wikipedia/en/9/95/Digital_India_logo.svg"
                        alt="Digital India"
                        className="h-10 bg-white p-1 rounded opacity-80"
                    />
                </div>
            </div>

            {/* Bottom Strip */}
            <div className="border-t border-gray-700 mt-8 pt-4 text-center">
                <p className="text-xs text-gray-400">
                    Website Content Managed by <strong>Department of Justice, Ministry of Law and Justice, Government of India</strong>
                </p>
                <p className="text-xs text-gray-500 mt-1">
                    Designed, Developed and Hosted by <a href="#" className="hover:text-white underline">National Informatics Centre (NIC)</a>
                </p>
                <p className="text-xs text-gray-600 mt-2">
                    Last Updated: {new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' })}
                </p>
            </div>
        </footer>
    );
};
