const fs = require('fs');
const path = require('path');
const { marked } = require('marked');

// Configuration
const CONFIG = {
  // Source markdown files
  markdownFiles: [
    {
      source: '../../evaluation/metrics_documentation.md',
      output: '../public/docs/metrics_documentation.html',
      title: 'Tham khảo: Tài liệu Tất cả Candidate Metrics'
    },
    {
      source: '../../evaluation/selected/selected_metrics_documentation.md',
      output: '../public/docs/selected_metrics_documentation.html',
      title: 'Tài liệu Chi tiết Các Chỉ số Được Lựa Chọn'
    },
    {
      source: '../../evaluation/selected/conclusion.md',
      output: '../public/docs/conclusion.html',
      title: 'Kết luận Đánh giá'
    },
    {
      source: '../../evaluation/selected/selected_report.md',
      output: '../public/docs/selected_report.html',
      title: 'Báo cáo Tổng hợp Các Chỉ số (Tóm tắt)'
    }
  ],
  // Dataset files (CSV)
  datasets: [
    {
      source: '../../data/adidas_cleaned.csv',
      output: '../public/docs/adidas_dataset.html',
      title: 'Tập dữ liệu Adidas',
      sourceUrl: 'https://www.kaggle.com/datasets/heemalichaudhari/adidas-sales-dataset',
      citation: 'Heemali Chaudhari. 2022. Adidas Sales Dataset (Adidas Sales in United States). Accessed on 29-Apr-2026.',
      description: 'Tập dữ liệu này chứa thông tin về doanh số bán hàng của Adidas, bao gồm các chi tiết về nhà bán lẻ, địa điểm, sản phẩm, giá, số lượng bán được, doanh thu và lợi nhuận hoạt động.'
    },
    {
      source: '../../data/employee_attrition_cleaned.csv',
      output: '../public/docs/employee_attrition_dataset.html',
      title: 'Tập dữ liệu Employee Attrition',
      sourceUrl: 'https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset',
      citation: 'Pavan Subhash. 2017. IBM HR Analytics Employee Attrition & Performance (Predict attrition of your valuable employees). Accessed on 29-Apr-2026.',
      description: 'Tập dữ liệu này chứa thông tin nhân sự của IBM, bao gồm các yếu tố ảnh hưởng đến việc nhân viên nghỉ việc như độ tuổi, mức lương, mức độ hài lòng với môi trường làm việc, v.v.'
    },
    {
      source: '../../data/online_sales_cleaned.csv',
      output: '../public/docs/online_sales_dataset.html',
      title: 'Tập dữ liệu Online Sales',
      sourceUrl: 'https://www.kaggle.com/datasets/shreyanshverma27/online-sales-dataset-popular-marketplace-data',
      citation: 'Shreyansh Verma. 2024. Online Sales Dataset - Popular Marketplace Data (Global Transactions Across Various Product Categories). Accessed on 29-Apr-2026.',
      description: 'Tập dữ liệu này chứa thông tin về các giao dịch bán hàng trực tuyến trên các sàn thương mại điện tử, bao gồm danh mục sản phẩm, số lượng, giá, doanh thu, khu vực và phương thức thanh toán.'
    }
  ],
  // Template files
  template: './template.html',
  dataTemplate: './data_template.html'
};

// Ensure output directory exists
function ensureDir(dir) {
  const fullPath = path.resolve(__dirname, dir);
  const dirname = path.dirname(fullPath);
  if (!fs.existsSync(dirname)) {
    fs.mkdirSync(dirname, { recursive: true });
  }
}

// Build a single markdown file to HTML
function buildMarkdownToHTML(config) {
  const sourcePath = path.resolve(__dirname, config.source);
  const outputPath = path.resolve(__dirname, config.output);
  const templatePath = path.resolve(__dirname, CONFIG.template);

  console.log(`Building: ${config.source} -> ${config.output}`);

  // Read markdown file
  const markdown = fs.readFileSync(sourcePath, 'utf-8');

  // Convert markdown to HTML
  const htmlContent = marked.parse(markdown);

  // Read template
  const template = fs.readFileSync(templatePath, 'utf-8');

  // Replace placeholders
  let finalHtml = template
    .replace('{{TITLE}}', config.title)
    .replace('{{CONTENT}}', htmlContent);

  // Ensure output directory exists
  ensureDir(config.output);

  // Write output file
  fs.writeFileSync(outputPath, finalHtml, 'utf-8');

  console.log(`✓ Generated: ${outputPath}`);
}

// Build CSV to HTML
function buildCSVToHTML(config) {
  const sourcePath = path.resolve(__dirname, config.source);
  const outputPath = path.resolve(__dirname, config.output);
  const templatePath = path.resolve(__dirname, CONFIG.dataTemplate);

  console.log(`Building: ${config.source} -> ${config.output}`);

  // Read CSV file
  const csvContent = fs.readFileSync(sourcePath, 'utf-8');
  const lines = csvContent.split('\n').filter(line => line.trim());
  
  // Take first 100 rows (including header)
  const rows = lines.slice(0, 101);
  
  // Parse CSV
  const headers = rows[0].split(';');
  const dataRows = rows.slice(1).map(row => row.split(';'));
  
  // Generate HTML table
  let tableHtml = '<table>\n<thead>\n<tr>\n';
  headers.forEach(header => {
    tableHtml += `<th>${header}</th>\n`;
  });
  tableHtml += '</tr>\n</thead>\n<tbody>\n';
  
  dataRows.forEach(row => {
    tableHtml += '<tr>\n';
    row.forEach(cell => {
      tableHtml += `<td>${cell}</td>\n`;
    });
    tableHtml += '</tr>\n';
  });
  tableHtml += '</tbody>\n</table>';
  
  // Read template
  const template = fs.readFileSync(templatePath, 'utf-8');
  
  // Replace placeholders (use replaceAll for global replacement)
  let finalHtml = template
    .replaceAll('{{TITLE}}', config.title)
    .replaceAll('{{SOURCE_URL}}', config.sourceUrl)
    .replaceAll('{{CITATION}}', config.citation)
    .replaceAll('{{DESCRIPTION}}', config.description)
    .replaceAll('{{DATA_TABLE}}', tableHtml);
  
  // Ensure output directory exists
  ensureDir(config.output);
  
  // Write output file
  fs.writeFileSync(outputPath, finalHtml, 'utf-8');
  
  console.log(`✓ Generated: ${outputPath}`);
}

// Build all markdown files
function buildAll() {
  console.log('Starting build process...\n');

  CONFIG.markdownFiles.forEach((config, index) => {
    try {
      buildMarkdownToHTML(config);
    } catch (error) {
      console.error(`✗ Error building ${config.source}:`, error.message);
    }
  });
  
  CONFIG.datasets.forEach((config, index) => {
    try {
      buildCSVToHTML(config);
    } catch (error) {
      console.error(`✗ Error building ${config.source}:`, error.message);
    }
  });

  console.log('\n✓ Build complete!');
}

// Run build
if (require.main === module) {
  buildAll();
}

module.exports = { buildAll, buildMarkdownToHTML };
