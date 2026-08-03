import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';

interface DocPageProps {
  params: {
    doc: string[];
  };
}

export async function getDocContent(docPath: string[]) {
  try {
    const docsDirectory = path.join(process.cwd(), 'docs');
    const fullPath = path.join(docsDirectory, `${docPath.join('/')}.md`);
    
    // Check if file exists
    if (!fs.existsSync(fullPath)) {
      return null;
    }
    
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const { data, content } = matter(fileContents);
    
    return {
      frontMatter: data,
      content,
      slug: docPath.join('/'),
    };
  } catch (error) {
    console.error('Error reading doc:', error);
    return null;
  }
}

export async function generateStaticParams() {
  try {
    const docsDirectory = path.join(process.cwd(), 'docs');
    const getAllMdFiles = (dir: string, basePath: string = ''): string[][] => {
      const files: string[][] = [];
      const items = fs.readdirSync(dir);
      
      for (const item of items) {
        const fullPath = path.join(dir, item);
        const stat = fs.statSync(fullPath);
        
        if (stat.isDirectory()) {
          files.push(...getAllMdFiles(fullPath, path.join(basePath, item)));
        } else if (item.endsWith('.md')) {
          const relativePath = path.join(basePath, item.replace('.md', ''));
          files.push(relativePath.split('/'));
        }
      }
      
      return files;
    };
    
    return getAllMdFiles(docsDirectory);
  } catch (error) {
    console.error('Error generating static params:', error);
    return [];
  }
}
