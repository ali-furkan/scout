import Link from 'next/link';

export function Header() {
    return (
        <header className="p-4 w-full backdrop-blur-lg bg-inherit dark:bg-inherit dark:bg-opacity-50 bg-opacity-30 z-10 sticky">
            <div className="mx-auto max-w-5xl flex justify-center items-center py-2">
                <nav className="flex space-x-4">
                    <Link href="/" className='text-gray-500 dark:hover:text-white hover:text-black'>Overview</Link>
                    <Link href="/matches" className='text-gray-500 dark:hover:text-white hover:text-black'>Fixtures</Link>
                    <Link href="/tables" className='text-gray-500 dark:hover:text-white hover:text-black'>Tables</Link>
                    <Link href="/model" className='text-gray-500 dark:hover:text-white hover:text-black'>Model</Link>
                </nav>
            </div>
        </header>
    )
}